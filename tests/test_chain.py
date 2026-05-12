import json
import subprocess
import sys
from pathlib import Path

from specoracle.cli import write_generation_result
from specoracle.config import ModelSettings, Task
from specoracle.evaluator import PytestResult
from specoracle.generator import GenerationResult, MockLLMClient
from specoracle.stress import SpecArena


def test_chain_depth_1_compat(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("specoracle.stress.run_pytest_for_code", _passing_pytest)
    task = _task()
    output = tmp_path / "run"
    write_generation_result(_generation(task), output)
    arena = _arena()

    results = arena.chain_run_dir(
        run_dir=output,
        task_map={task.id: task},
        chain_depth=1,
    )

    assert results == []
    assert not list(output.rglob("chain_results.json"))


def test_chain_depth_3_artifacts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("specoracle.stress.run_pytest_for_code", _passing_pytest)
    task = _task()
    output = tmp_path / "run"
    write_generation_result(_generation(task), output)
    arena = _arena()

    results = arena.chain_run_dir(
        run_dir=output,
        task_map={task.id: task},
        chain_depth=3,
    )

    assert [result.step for result in results] == [1, 2, 3]
    assert all(result.pass_bool for result in results)
    assert all(result.token_estimate > 0 for result in results)
    assert all(result.accumulated_score > 0 for result in results)
    chain_path = next(output.rglob("chain_results.json"))
    payload = json.loads(chain_path.read_text(encoding="utf-8"))
    assert len(payload["steps"]) == 3


def test_analyze_chain_null_and_signal(tmp_path: Path) -> None:
    null_path = tmp_path / "null.json"
    null_path.write_text(
        json.dumps(
            [
                _row("baseline_generation", 1, True, 10_000),
                _row("oracle_generation", 1, True, 10_000),
            ]
        ),
        encoding="utf-8",
    )
    null_result = subprocess.run(
        [sys.executable, "scripts/analyze_chain.py", str(null_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "THRESHOLD_FOUND: False" in null_result.stdout

    signal_path = tmp_path / "signal.json"
    signal_path.write_text(
        json.dumps(
            [
                _row("baseline_generation", 2, False, 75_000),
                _row("oracle_generation", 2, True, 75_000),
            ]
        ),
        encoding="utf-8",
    )
    signal_result = subprocess.run(
        [sys.executable, "scripts/analyze_chain.py", str(signal_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "THRESHOLD_FOUND: True" in signal_result.stdout
    assert "THRESHOLD_BAND: MED" in signal_result.stdout


def _arena() -> SpecArena:
    settings = ModelSettings(
        provider="mock",
        model="mock-local",
        temperature=0.8,
        max_tokens=128,
        timeout_seconds=1,
        api_key_env="SPECORACLE_NO_API_KEY",
    )
    return SpecArena(client=MockLLMClient(), settings=settings, pytest_timeout_seconds=1)


def _task() -> Task:
    return Task(
        id="answer",
        entry_point="answer",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt='Add answer_text() -> str returning "42".',
        day2_test_code=(
            "from solution import answer, answer_text\n\n\n"
            "def test_day2():\n"
            "    assert answer() == 42\n"
            "    assert answer_text() == '42'\n"
        ),
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
        mock_day2_solution="def answer():\n    return 42\n\n\ndef answer_text():\n    return '42'\n",
    )


def _generation(task: Task) -> GenerationResult:
    code = "def answer():\n    return 42\n"
    return GenerationResult(
        task_id=task.id,
        mode="baseline",
        variant="baseline_generation",
        provider="mock",
        model="mock-local",
        sample_index=0,
        requested_temperature=0.8,
        effective_temperature=0.8,
        entry_point=task.entry_point,
        task=task.to_mapping(),
        oracle_spec="zen",
        oracle_spec_label="zen_of_python",
        code=code,
        raw_response=code,
        system_prompt="",
        user_prompt="",
    )


def _passing_pytest(*args, **kwargs) -> PytestResult:
    return PytestResult(
        passed=True,
        exit_code=0,
        duration_seconds=0.01,
        timed_out=False,
        sandbox="unit",
        stdout="",
        stderr="",
    )


def _row(variant: str, step: int, passed: bool, score: int) -> dict[str, object]:
    return {
        "step": step,
        "task_id": "answer",
        "variant": variant,
        "provider": "mock",
        "model": "mock-local",
        "sample_index": 0,
        "maintenance_provider": "mock",
        "maintenance_model": "mock-local",
        "pass_bool": passed,
        "token_estimate": 1000,
        "cc_average": 5.0,
        "nesting_depth": 1,
        "function_count": 1,
        "elapsed_seconds": 0.1,
        "accumulated_score": score,
        "failure_type": "none" if passed else "assertion_failure",
        "failure_detail": "",
        "raw_response": "",
        "code": "def answer():\n    return 42\n",
    }
