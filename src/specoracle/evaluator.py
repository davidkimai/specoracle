from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import statistics
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from radon.complexity import cc_visit
from radon.metrics import mi_visit

from specoracle.config import (
    JUDGE_SYSTEM_PROMPT,
    JUDGE_USER_TEMPLATE,
    ModelSettings,
    Task,
    oracle_spec_for_task,
    oracle_spec_label_for_task,
)
from specoracle.generator import LLMClient

DEFAULT_PYTEST_DOCKER_IMAGE = "specoracle-pytest:py311-alpine"
PYTEST_SANDBOX_BASE_IMAGE = "python:3.11-alpine"
PYTEST_SANDBOX_PYTEST_VERSION = "9.0.2"
PYTEST_DOCKERFILE = """\
FROM python:3.11-alpine
ENV PYTHONDONTWRITEBYTECODE=1
RUN python -m pip install --no-cache-dir pytest==9.0.2
WORKDIR /work
"""


@dataclass(frozen=True)
class StaticMetrics:
    syntax_ok: bool
    syntax_error: str | None
    loc: int
    function_count: int
    class_count: int
    cyclomatic_complexity_total: int
    cyclomatic_complexity_average: float
    cyclomatic_complexity_max: int
    maintainability_index: float | None
    max_nesting_depth: int


@dataclass(frozen=True)
class PytestResult:
    passed: bool
    exit_code: int
    duration_seconds: float
    timed_out: bool
    sandbox: str
    stdout: str
    stderr: str
    sandbox_error: str | None = None


@dataclass(frozen=True)
class JudgeResult:
    skipped: bool
    score: int | None
    rationale: str
    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    raw_response: str = ""
    error: str | None = None


@dataclass(frozen=True)
class EvaluationResult:
    task_id: str
    variant: str
    provider: str
    model: str
    sample_index: int
    requested_temperature: float | None
    effective_temperature: float | None
    oracle_spec: str
    oracle_spec_label: str
    static_metrics: StaticMetrics
    pytest: PytestResult
    judge: JudgeResult = field(default_factory=lambda: JudgeResult(True, None, "not requested"))

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


class _AstSummaryVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.function_count = 0
        self.class_count = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_count += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_count += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_count += 1
        self.generic_visit(node)


class _NestingDepthVisitor(ast.NodeVisitor):
    _CONTROL_NODES = (
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.With,
        ast.AsyncWith,
        ast.Try,
        ast.ExceptHandler,
        ast.Match,
    )

    def __init__(self) -> None:
        self.current_depth = 0
        self.max_depth = 0

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, self._CONTROL_NODES):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            super().generic_visit(node)
            self.current_depth -= 1
            return
        super().generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self._visit_if(node, is_elif=False)

    def _visit_if(self, node: ast.If, *, is_elif: bool) -> None:
        if not is_elif:
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)

        for child in node.body:
            self.visit(child)

        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            self._visit_if(node.orelse[0], is_elif=True)
        else:
            for child in node.orelse:
                self.visit(child)

        if not is_elif:
            self.current_depth -= 1


def compute_static_metrics(code: str) -> StaticMetrics:
    loc = len([line for line in code.splitlines() if line.strip()])
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return StaticMetrics(
            syntax_ok=False,
            syntax_error=f"{exc.msg} at line {exc.lineno}",
            loc=loc,
            function_count=0,
            class_count=0,
            cyclomatic_complexity_total=0,
            cyclomatic_complexity_average=0.0,
            cyclomatic_complexity_max=0,
            maintainability_index=None,
            max_nesting_depth=0,
        )

    summary = _AstSummaryVisitor()
    summary.visit(tree)

    nesting = _NestingDepthVisitor()
    nesting.visit(tree)

    blocks = cc_visit(code)
    complexities = [int(block.complexity) for block in blocks]
    total_cc = sum(complexities)
    max_cc = max(complexities, default=0)
    avg_cc = total_cc / len(complexities) if complexities else 0.0

    return StaticMetrics(
        syntax_ok=True,
        syntax_error=None,
        loc=loc,
        function_count=summary.function_count,
        class_count=summary.class_count,
        cyclomatic_complexity_total=total_cc,
        cyclomatic_complexity_average=round(avg_cc, 3),
        cyclomatic_complexity_max=max_cc,
        maintainability_index=round(float(mi_visit(code, multi=True)), 3),
        max_nesting_depth=nesting.max_depth,
    )


def run_pytest_for_code(
    code: str,
    test_code: str,
    *,
    timeout_seconds: float = 10.0,
    docker_image: str | None = None,
    memory_limit: str = "256m",
    cpus: str = "1.0",
) -> PytestResult:
    start = time.monotonic()
    image = docker_image or os.getenv("SPECORACLE_PYTEST_IMAGE", DEFAULT_PYTEST_DOCKER_IMAGE)
    try:
        _ensure_docker_pytest_image(image)
    except (RuntimeError, subprocess.SubprocessError) as exc:
        return PytestResult(
            passed=False,
            exit_code=125,
            duration_seconds=round(time.monotonic() - start, 3),
            timed_out=False,
            sandbox=f"docker:{image}",
            stdout="",
            stderr="",
            sandbox_error=str(exc),
        )

    with tempfile.TemporaryDirectory(prefix="specoracle_pytest_") as temp_dir:
        temp_path = Path(temp_dir)
        solution_path = temp_path / "solution.py"
        test_path = temp_path / "test_solution.py"
        solution_path.write_text(code, encoding="utf-8")
        test_path.write_text(test_code, encoding="utf-8")
        os.chmod(temp_path, 0o755)
        os.chmod(solution_path, 0o644)
        os.chmod(test_path, 0o644)

        command = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--memory",
            memory_limit,
            "--cpus",
            cpus,
            "--pids-limit",
            "128",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=64m,mode=1777",
            "--user",
            "65534:65534",
            "-e",
            "HOME=/tmp",
            "-e",
            "PYTHONDONTWRITEBYTECODE=1",
            "-e",
            "PYTHONPYCACHEPREFIX=/tmp/pycache",
            "--mount",
            f"type=bind,source={temp_path},target=/work,readonly",
            "-w",
            "/work",
            image,
            "python",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "test_solution.py",
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return PytestResult(
                passed=False,
                exit_code=124,
                duration_seconds=round(time.monotonic() - start, 3),
                timed_out=True,
                sandbox=f"docker:{image}",
                stdout=_coerce_output(exc.stdout),
                stderr=_coerce_output(exc.stderr),
            )

    return PytestResult(
        passed=completed.returncode == 0,
        exit_code=completed.returncode,
        duration_seconds=round(time.monotonic() - start, 3),
        timed_out=False,
        sandbox=f"docker:{image}",
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def judge_code(
    *,
    task: Task,
    code: str,
    oracle_spec: str,
    client: LLMClient | None,
    settings: ModelSettings | None,
) -> JudgeResult:
    if client is None or settings is None:
        return JudgeResult(skipped=True, score=None, rationale="not requested")

    prompt = JUDGE_USER_TEMPLATE.format(
        task_id=task.id,
        entry_point=task.entry_point,
        prompt=task.prompt.strip(),
        oracle_spec=oracle_spec.strip(),
        code=code,
    )
    try:
        raw = client.complete(
            system_prompt=JUDGE_SYSTEM_PROMPT,
            user_prompt=prompt,
            settings=settings,
        )
        payload = _parse_judge_json(raw)
        score = int(payload["score"])
        score = min(10, max(1, score))
        return JudgeResult(
            skipped=False,
            score=score,
            rationale=str(payload.get("rationale") or ""),
            strengths=tuple(str(item) for item in payload.get("strengths", ())),
            weaknesses=tuple(str(item) for item in payload.get("weaknesses", ())),
            raw_response=raw,
            error=None,
        )
    except Exception as exc:  # Judge failures should not erase static/test evidence.
        return JudgeResult(
            skipped=False,
            score=None,
            rationale="judge failed",
            raw_response=locals().get("raw", ""),
            error=str(exc),
        )


def evaluate_code(
    *,
    task: Task,
    code: str,
    variant: str,
    provider: str,
    model: str,
    sample_index: int = 0,
    requested_temperature: float | None = None,
    effective_temperature: float | None = None,
    oracle_spec: str | None = None,
    oracle_spec_label: str | None = None,
    pytest_timeout_seconds: float,
    judge_client: LLMClient | None = None,
    judge_settings: ModelSettings | None = None,
) -> EvaluationResult:
    active_oracle_spec = oracle_spec or oracle_spec_for_task(task)
    active_oracle_label = oracle_spec_label or oracle_spec_label_for_task(task)
    return EvaluationResult(
        task_id=task.id,
        variant=variant,
        provider=provider,
        model=model,
        sample_index=sample_index,
        requested_temperature=requested_temperature,
        effective_temperature=effective_temperature,
        oracle_spec=active_oracle_spec,
        oracle_spec_label=active_oracle_label,
        static_metrics=compute_static_metrics(code),
        pytest=run_pytest_for_code(
            code,
            task.test_code,
            timeout_seconds=pytest_timeout_seconds,
        ),
        judge=judge_code(
            task=task,
            code=code,
            oracle_spec=active_oracle_spec,
            client=judge_client,
            settings=judge_settings,
        ),
    )


def _parse_judge_json(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end < start:
            raise
        payload = json.loads(raw[start : end + 1])

    if not isinstance(payload, dict):
        raise ValueError("judge response must be a JSON object")
    if "score" not in payload:
        raise ValueError("judge response is missing score")
    return payload


def _coerce_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _ensure_docker_pytest_image(image: str) -> None:
    if shutil.which("docker") is None:
        raise RuntimeError("docker executable was not found on PATH")

    inspected = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        text=True,
        check=False,
    )
    if inspected.returncode == 0:
        return

    raise RuntimeError(
        f"Docker pytest sandbox image {image!r} was not found. "
        "Run `specoracle sandbox prepare` before evaluation."
    )


def prepare_pytest_sandbox(*, image: str = DEFAULT_PYTEST_DOCKER_IMAGE) -> None:
    if shutil.which("docker") is None:
        raise RuntimeError("docker executable was not found on PATH")

    inspected = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        text=True,
        check=False,
    )
    if inspected.returncode == 0:
        return

    dockerfile_text = PYTEST_DOCKERFILE.replace(
        "python:3.11-alpine",
        PYTEST_SANDBOX_BASE_IMAGE,
    ).replace(
        "pytest==9.0.2",
        f"pytest=={PYTEST_SANDBOX_PYTEST_VERSION}",
    )
    with tempfile.TemporaryDirectory(prefix="specoracle_docker_build_") as temp_dir:
        dockerfile = Path(temp_dir) / "Dockerfile"
        dockerfile.write_text(dockerfile_text, encoding="utf-8")
        built = subprocess.run(
            ["docker", "build", "-t", image, temp_dir],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    if built.returncode != 0:
        detail = (built.stderr or built.stdout).strip()
        raise RuntimeError(f"failed to build Docker pytest image {image}: {detail}")


def benchmark_pytest_sandbox(
    *,
    iterations: int = 5,
    timeout_seconds: float = 10.0,
    image: str = DEFAULT_PYTEST_DOCKER_IMAGE,
) -> dict[str, float | int | str | bool]:
    durations: list[float] = []
    failures = 0
    for _ in range(iterations):
        result = run_pytest_for_code(
            "def answer():\n    return 42\n",
            "from solution import answer\n\n\ndef test_answer():\n    assert answer() == 42\n",
            timeout_seconds=timeout_seconds,
            docker_image=image,
        )
        durations.append(result.duration_seconds)
        if not result.passed:
            failures += 1

    return {
        "image": image,
        "iterations": iterations,
        "failures": failures,
        "all_passed": failures == 0,
        "median_seconds": round(statistics.median(durations), 3),
        "min_seconds": round(min(durations), 3),
        "max_seconds": round(max(durations), 3),
    }
