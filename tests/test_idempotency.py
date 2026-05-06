import json
from pathlib import Path

import pytest

from specoracle.cli import generate_tasks, write_generation_result
from specoracle.config import ModelSettings, Task
from specoracle.generator import GenerationResult, SpecOracleGenerator
from specoracle.stress import SpecArena, StressResult, write_stress_result


class StaticClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0
        self.last_effective_temperature = 0.8

    def complete(self, **_: object) -> str:
        self.calls += 1
        return self.response


class ExplodingClient:
    last_effective_temperature = 0.8

    def complete(self, **_: object) -> str:
        raise AssertionError("LLM should not be called for reused artifacts")


def test_generate_tasks_reuses_complete_artifact_without_llm_call(tmp_path: Path) -> None:
    task = _task()
    output = tmp_path / "run"
    settings = _settings(model="unit")
    first_client = StaticClient("def answer():\n    return 42\n")
    first_generator = SpecOracleGenerator(first_client, settings)

    first = generate_tasks(first_generator, [task], output, modes=("baseline",), samples=1)
    assert len(first) == 1
    assert first_client.calls == 1

    second_generator = SpecOracleGenerator(ExplodingClient(), settings)
    second = generate_tasks(second_generator, [task], output, modes=("baseline",), samples=1)

    assert len(second) == 1
    assert second[0].code == first[0].code


def test_generate_tasks_rejects_partial_artifact(tmp_path: Path) -> None:
    task = _task()
    output = tmp_path / "run"
    settings = _settings(model="unit")
    generator = SpecOracleGenerator(StaticClient("def answer():\n    return 42\n"), settings)
    generate_tasks(generator, [task], output, modes=("baseline",), samples=1)
    next(output.rglob("solution.py")).unlink()

    with pytest.raises(RuntimeError, match="partial generation artifact"):
        generate_tasks(generator, [task], output, modes=("baseline",), samples=1)


def test_generate_tasks_rejects_mismatched_artifact_key(tmp_path: Path) -> None:
    task = _task()
    output = tmp_path / "run"
    settings = _settings(model="unit")
    generator = SpecOracleGenerator(StaticClient("def answer():\n    return 42\n"), settings)
    generate_tasks(generator, [task], output, modes=("baseline",), samples=1)

    generation_path = next(output.rglob("generation.json"))
    payload = json.loads(generation_path.read_text(encoding="utf-8"))
    payload["model"] = "other-model"
    generation_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="generation artifact key mismatch"):
        generate_tasks(generator, [task], output, modes=("baseline",), samples=1)


def test_generate_tasks_rejects_mismatched_temperature(tmp_path: Path) -> None:
    task = _task()
    output = tmp_path / "run"
    settings = _settings(model="unit")
    generator = SpecOracleGenerator(StaticClient("def answer():\n    return 42\n"), settings)
    generate_tasks(generator, [task], output, modes=("baseline",), samples=1)

    generation_path = next(output.rglob("generation.json"))
    payload = json.loads(generation_path.read_text(encoding="utf-8"))
    payload["requested_temperature"] = 0.2
    generation_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="generation artifact temperature mismatch"):
        generate_tasks(generator, [task], output, modes=("baseline",), samples=1)


def test_stress_reuses_complete_artifact_without_llm_call(tmp_path: Path) -> None:
    task = _task()
    output = tmp_path / "run"
    generation = _generation_result(task)
    artifact_dir = write_generation_result(generation, output)
    write_stress_result(_stress_result(generation, context=True), artifact_dir)

    arena = SpecArena(
        client=ExplodingClient(),
        settings=_settings(model="unit-maintenance"),
        pytest_timeout_seconds=1,
    )
    results = arena.stress_run_dir(
        run_dir=output,
        task_map={task.id: task},
        context_ablation=True,
    )

    assert len(results) == 1
    assert results[0].maintenance_token_overhead == 5
    assert results[0].context_ablation_pass_at_1 is True


def test_stress_rejects_existing_artifact_without_required_context_ablation(
    tmp_path: Path,
) -> None:
    task = _task()
    output = tmp_path / "run"
    generation = _generation_result(task)
    artifact_dir = write_generation_result(generation, output)
    write_stress_result(_stress_result(generation, context=False), artifact_dir)

    arena = SpecArena(
        client=ExplodingClient(),
        settings=_settings(model="unit-maintenance"),
        pytest_timeout_seconds=1,
    )

    with pytest.raises(RuntimeError, match="missing context ablation"):
        arena.stress_run_dir(
            run_dir=output,
            task_map={task.id: task},
            context_ablation=True,
        )


def test_stress_rejects_mismatched_artifact_key(tmp_path: Path) -> None:
    task = _task()
    output = tmp_path / "run"
    generation = _generation_result(task)
    artifact_dir = write_generation_result(generation, output)
    write_stress_result(_stress_result(generation, context=True), artifact_dir)

    stress_path = artifact_dir / "stress.json"
    payload = json.loads(stress_path.read_text(encoding="utf-8"))
    payload["sample_index"] = 99
    stress_path.write_text(json.dumps(payload), encoding="utf-8")

    arena = SpecArena(
        client=ExplodingClient(),
        settings=_settings(model="unit-maintenance"),
        pytest_timeout_seconds=1,
    )

    with pytest.raises(RuntimeError, match="stress artifact key mismatch"):
        arena.stress_run_dir(
            run_dir=output,
            task_map={task.id: task},
            context_ablation=True,
        )


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
        day2_stressors=("interface_generalization", "backwards_compatibility"),
        human_reference="def answer():\n    return 42\n",
    )


def _settings(*, model: str) -> ModelSettings:
    return ModelSettings(
        provider="mock",
        model=model,
        temperature=0.8,
        max_tokens=128,
        timeout_seconds=1,
        api_key_env="SPECORACLE_NO_API_KEY",
        require_temperature=True,
    )


def _generation_result(task: Task) -> GenerationResult:
    return GenerationResult(
        task_id=task.id,
        mode="baseline",
        variant="baseline_generation",
        provider="mock",
        model="unit",
        sample_index=0,
        requested_temperature=0.8,
        effective_temperature=0.8,
        entry_point=task.entry_point,
        task=task.to_mapping(),
        oracle_spec="zen",
        oracle_spec_label="zen_of_python",
        code="def answer():\n    return 42\n",
        raw_response="def answer():\n    return 42\n",
        system_prompt="",
        user_prompt="",
    )


def _stress_result(generation: GenerationResult, *, context: bool) -> StressResult:
    return StressResult(
        task_id=generation.task_id,
        variant=generation.variant,
        provider=generation.provider,
        model=generation.model,
        sample_index=generation.sample_index,
        requested_temperature=generation.requested_temperature,
        effective_temperature=generation.effective_temperature,
        oracle_spec=generation.oracle_spec,
        oracle_spec_label=generation.oracle_spec_label,
        maintenance_provider="mock",
        maintenance_model="unit-maintenance",
        pass_at_1=True,
        duration_seconds=0.1,
        maintenance_token_overhead=5,
        maintenance_failure_type="none",
        maintenance_failure_detail="",
        context_ablation_pass_at_1=True if context else None,
        context_ablation_token_overhead=4 if context else None,
        context_ablation_failure_type="none" if context else None,
        context_ablation_failure_detail="" if context else None,
        pytest=None,
        raw_response="def answer():\n    return 42\n\n\ndef answer_text():\n    return '42'\n",
        code="def answer():\n    return 42\n\n\ndef answer_text():\n    return '42'\n",
        error=None,
    )
