from specoracle.config import ModelSettings, Task
from specoracle.evaluator import (
    DEFAULT_PYTEST_DOCKER_IMAGE,
    compute_static_metrics,
    evaluate_code,
    prepare_pytest_sandbox,
    run_pytest_for_code,
)
from specoracle.generator import MockLLMClient


class RecordingJudgeClient:
    def __init__(self) -> None:
        self.user_prompt = ""

    def complete(self, *, system_prompt: str, user_prompt: str, settings: ModelSettings) -> str:
        self.user_prompt = user_prompt
        return (
            '{"score": 7, "rationale": "custom spec considered", '
            '"strengths": [], "weaknesses": []}'
        )


def test_static_metrics_counts_complexity_and_nesting() -> None:
    code = """
def classify(items):
    result = []
    for item in items:
        if item > 0:
            result.append("positive")
        else:
            result.append("other")
    return result
"""

    metrics = compute_static_metrics(code)

    assert metrics.syntax_ok
    assert metrics.function_count == 1
    assert metrics.cyclomatic_complexity_max >= 3
    assert metrics.maintainability_index is not None
    assert metrics.max_nesting_depth >= 2


def test_static_metrics_treats_elif_chain_as_one_depth() -> None:
    code = """
def classify(value):
    if value == 1:
        return "one"
    elif value == 2:
        return "two"
    elif value == 3:
        return "three"
    else:
        return "other"
"""

    metrics = compute_static_metrics(code)

    assert metrics.syntax_ok
    assert metrics.max_nesting_depth == 1


def test_pytest_runner_pass_fail_and_timeout_paths() -> None:
    prepare_pytest_sandbox(image=DEFAULT_PYTEST_DOCKER_IMAGE)

    passing = run_pytest_for_code(
        "def answer():\n    return 42\n",
        "from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        timeout_seconds=10,
    )
    failing = run_pytest_for_code(
        "def answer():\n    return 0\n",
        "from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        timeout_seconds=10,
    )
    timeout = run_pytest_for_code(
        "def spin():\n    while True:\n        pass\n",
        "from solution import spin\n\ndef test_spin():\n    spin()\n",
        timeout_seconds=1.5,
    )

    assert passing.passed
    assert passing.sandbox.startswith("docker:")
    assert not failing.passed
    assert timeout.timed_out


def test_pytest_runner_fails_cleanly_when_sandbox_image_missing() -> None:
    result = run_pytest_for_code(
        "def answer():\n    return 42\n",
        "from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        docker_image="specoracle-missing-image:phase3-test",
    )

    assert not result.passed
    assert result.exit_code == 125
    assert result.sandbox_error is not None
    assert "specoracle sandbox prepare" in result.sandbox_error


def test_evaluate_code_with_mock_judge() -> None:
    prepare_pytest_sandbox(image=DEFAULT_PYTEST_DOCKER_IMAGE)

    task = Task(
        id="answer",
        entry_point="answer",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text() -> str returning '42'.",
        day2_test_code=(
            "from solution import answer_text\n\n"
            "def test_answer_text():\n    assert answer_text() == '42'\n"
        ),
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
        custom_spec_override="Prefer direct single-expression functions.",
    )

    result = evaluate_code(
        task=task,
        code="def answer():\n    return 42\n",
        variant="oracle_generation",
        provider="mock",
        model="mock-local",
        pytest_timeout_seconds=10,
        judge_client=MockLLMClient(),
        judge_settings=ModelSettings(provider="mock", model="mock-local"),
    )

    assert result.pytest.passed
    assert result.judge.score == 8
    assert result.oracle_spec == "Prefer direct single-expression functions."


def test_judge_prompt_uses_active_custom_spec() -> None:
    prepare_pytest_sandbox(image=DEFAULT_PYTEST_DOCKER_IMAGE)

    task = Task(
        id="answer",
        entry_point="answer",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text() -> str returning '42'.",
        day2_test_code=(
            "from solution import answer_text\n\n"
            "def test_answer_text():\n    assert answer_text() == '42'\n"
        ),
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
        custom_spec_override="Use palindrome variable names for auditability.",
    )
    judge = RecordingJudgeClient()

    result = evaluate_code(
        task=task,
        code="def answer():\n    return 42\n",
        variant="oracle_generation",
        provider="mock",
        model="mock-local",
        pytest_timeout_seconds=10,
        judge_client=judge,
        judge_settings=ModelSettings(provider="mock", model="mock-local"),
    )

    assert result.judge.score == 7
    assert "Use palindrome variable names" in judge.user_prompt
