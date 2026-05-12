from pathlib import Path

from specoracle.cli import load_tasks
from specoracle.config import ModelSettings, Task
from specoracle.evaluator import PytestResult
from specoracle.hybrid import HybridConstraints, HybridOracle


class SequenceClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.prompts: list[str] = []
        self.last_effective_temperature = 0.8

    def complete(self, *, system_prompt: str, user_prompt: str, settings: ModelSettings) -> str:
        self.prompts.append(user_prompt)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


def test_hybrid_pass_zero_retries(monkeypatch) -> None:
    monkeypatch.setattr("specoracle.hybrid.run_pytest_for_code", _passing_pytest)
    client = SequenceClient([_low_cc_code()])
    oracle = HybridOracle(
        client=client,
        settings=_settings(),
        constraints=HybridConstraints(max_cc=10, max_nesting=3, require_pytest=True),
    )

    result = oracle.generate_with_gates(task=_task())

    assert result.hybrid
    assert result.hybrid["hybrid_retries"] == 0
    assert result.hybrid["hybrid_gate_pass"] is True
    assert result.hybrid["hard_cc_pass"] is True


def test_hybrid_cc_fail_retry_uses_specific_feedback(monkeypatch) -> None:
    monkeypatch.setattr("specoracle.hybrid.run_pytest_for_code", _passing_pytest)
    client = SequenceClient([_high_cc_code(), _low_cc_code()])
    oracle = HybridOracle(
        client=client,
        settings=_settings(),
        constraints=HybridConstraints(max_cc=3, max_nesting=10, require_pytest=True),
    )

    result = oracle.generate_with_gates(task=_task())

    assert result.hybrid
    assert result.hybrid["hybrid_retries"] == 1
    assert result.hybrid["hybrid_gate_pass"] is True
    assert result.hybrid["hybrid_feedback_cc_delta"] < 0
    assert "Cyclomatic complexity" in client.prompts[1]
    assert "Extract each logical path into a named helper" in client.prompts[1]


def test_hybrid_nesting_fail_retry_uses_specific_feedback(monkeypatch) -> None:
    monkeypatch.setattr("specoracle.hybrid.run_pytest_for_code", _passing_pytest)
    client = SequenceClient([_nested_code(), _low_cc_code()])
    oracle = HybridOracle(
        client=client,
        settings=_settings(),
        constraints=HybridConstraints(max_cc=10, max_nesting=1, require_pytest=True),
    )

    oracle.generate_with_gates(task=_task())

    assert "Replace nested conditionals with early returns or guard clauses" in client.prompts[1]


def test_hybrid_pytest_fail_retry_includes_test_output(monkeypatch) -> None:
    calls = 0

    def fake_pytest(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return _pytest(False, stdout="AssertionError: expected 42")
        return _pytest(True)

    monkeypatch.setattr("specoracle.hybrid.run_pytest_for_code", fake_pytest)
    client = SequenceClient([_low_cc_code(), _low_cc_code()])
    oracle = HybridOracle(
        client=client,
        settings=_settings(),
        constraints=HybridConstraints(max_cc=10, max_nesting=3, require_pytest=True),
    )

    oracle.generate_with_gates(task=_task())

    assert "Pytest failed" in client.prompts[1]
    assert "AssertionError: expected 42" in client.prompts[1]


def test_hybrid_adversarial_task_045_detects_spec_gate_conflict(monkeypatch) -> None:
    monkeypatch.setattr("specoracle.hybrid.run_pytest_for_code", _passing_pytest)
    task = next(
        task
        for task in load_tasks(Path("data/slopbench"))
        if task.id == "adversarial_spec"
    )
    client = SequenceClient([_very_high_cc_transition()])
    oracle = HybridOracle(
        client=client,
        settings=_settings(model="unit-adversarial"),
        constraints=HybridConstraints(max_cc=10, max_nesting=10, require_pytest=True, max_retries=2),
    )

    result = oracle.generate_with_gates(task=task)

    assert result.hybrid
    assert result.hybrid["hybrid_retries"] == 2
    assert result.hybrid["max_retries_exceeded"] is True
    assert result.hybrid["hard_cc_pass"] is False
    assert result.hybrid["hybrid_gate_pass"] is False


def _settings(model: str = "unit") -> ModelSettings:
    return ModelSettings(
        provider="openai",
        model=model,
        temperature=0.8,
        max_tokens=128,
        timeout_seconds=1,
        api_key_env="OPENAI_API_KEY",
        require_temperature=True,
    )


def _task() -> Task:
    return Task(
        id="answer",
        entry_point="answer",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text().",
        day2_test_code="def test_placeholder():\n    assert True\n",
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
    )


def _passing_pytest(*args, **kwargs) -> PytestResult:
    return _pytest(True)


def _pytest(passed: bool, stdout: str = "") -> PytestResult:
    return PytestResult(
        passed=passed,
        exit_code=0 if passed else 1,
        duration_seconds=0.01,
        timed_out=False,
        sandbox="unit",
        stdout=stdout,
        stderr="",
    )


def _low_cc_code() -> str:
    return "def answer():\n    return 42\n"


def _high_cc_code() -> str:
    return """\
def answer(x=0):
    if x == 1:
        return 1
    if x == 2:
        return 2
    if x == 3:
        return 3
    if x == 4:
        return 4
    return 42
"""


def _nested_code() -> str:
    return """\
def answer(x=0):
    if x >= 0:
        if x <= 10:
            if x != 5:
                return 42
    return 42
"""


def _very_high_cc_transition() -> str:
    branches = "\n".join(
        f"    if state == 's{i}' and event == 'e{i}':\n        return 's{i + 1}'"
        for i in range(18)
    )
    return f"def transition_state(state, event):\n{branches}\n    return state\n"
