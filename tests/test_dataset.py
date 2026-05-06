from pathlib import Path

from specoracle.cli import load_tasks
from specoracle.config import ZEN_ORACLE_SPEC, ModelSettings, Task
from specoracle.evaluator import (
    DEFAULT_PYTEST_DOCKER_IMAGE,
    evaluate_code,
    prepare_pytest_sandbox,
    run_pytest_for_code,
)


DATASET = Path(__file__).resolve().parents[1] / "data" / "slopbench_min"
DESIGN_NOTES = Path(__file__).resolve().parents[1] / "data" / "DESIGN_NOTES.md"


class RecordingJudgeClient:
    def __init__(self) -> None:
        self.user_prompt = ""

    def complete(self, *, system_prompt: str, user_prompt: str, settings: ModelSettings) -> str:
        self.user_prompt = user_prompt
        return '{"score": 9, "rationale": "active spec used", "strengths": [], "weaknesses": []}'


def test_slopbench_min_has_phase4_coverage() -> None:
    tasks = load_tasks(DATASET)
    tags = {tag for task in tasks for tag in task.tags}

    assert len(tasks) == 20
    assert sum(1 for task in tasks if task.custom_spec_override) >= 3
    assert sum(1 for task in tasks if "day2-hard" in task.tags) >= 8
    assert {"concurrency", "config_parsing", "cli_tool", "data_pipeline", "retry_backoff", "json"} <= tags
    design_notes = DESIGN_NOTES.read_text(encoding="utf-8")
    for task in tasks:
        assert task.day2_stressors
        for stressor in task.day2_stressors:
            assert f"`{stressor}`" in design_notes
        assert task.human_reference
        assert task.day2_prompt
        assert task.day2_test_code
        assert task.mock_solution
        assert task.mock_day2_solution


def test_slopbench_min_reference_and_mock_fixtures_pass_docker_pytest() -> None:
    prepare_pytest_sandbox(image=DEFAULT_PYTEST_DOCKER_IMAGE)
    failures = []

    for task in load_tasks(DATASET):
        fixtures = [
            ("human_reference", task.human_reference, task.test_code),
            ("mock_solution", task.mock_solution or "", task.test_code),
            ("mock_day2_solution", task.mock_day2_solution or "", task.day2_test_code),
        ]
        for name, code, test_code in fixtures:
            result = run_pytest_for_code(code, test_code, timeout_seconds=10)
            if not result.passed:
                failures.append((task.id, name, result.stdout, result.stderr, result.sandbox_error))

    assert failures == []


def test_custom_spec_judge_prompt_omits_zen_for_custom_task() -> None:
    prepare_pytest_sandbox(image=DEFAULT_PYTEST_DOCKER_IMAGE)

    task = Task(
        id="custom",
        prompt="Implement answer().",
        test_code="from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text().",
        day2_test_code="def test_placeholder():\n    assert True\n",
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
        custom_spec_override="Novel House Spec: use visible ledger variables.",
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

    assert result.judge.score == 9
    assert "Novel House Spec" in judge.user_prompt
    assert ZEN_ORACLE_SPEC not in judge.user_prompt
