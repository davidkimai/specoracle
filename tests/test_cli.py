import json
from pathlib import Path

from specoracle.cli import main


def test_cli_run_with_mock_provider(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    output = tmp_path / "run"
    dataset.mkdir()
    (dataset / "task.yaml").write_text(
        """
id: answer
entry_point: answer
prompt: |
  Implement answer() -> int returning 42.
test_code: |
  from solution import answer

  def test_answer():
      assert answer() == 42
day2_prompt: |
  Add answer_text() -> str returning "42".
day2_test_code: |
  from solution import answer, answer_text

  def test_original_and_day2_behavior():
      assert answer() == 42
      assert answer_text() == "42"
day2_stressors: [interface_generalization, backwards_compatibility]
human_reference: |
  def answer():
      return 42
mock_solution: |
  def answer():
      return 42
mock_day2_solution: |
  def answer():
      return 42


  def answer_text():
      return "42"
""".lstrip(),
        encoding="utf-8",
    )

    assert main(["sandbox", "prepare"]) == 0

    exit_code = main(
        [
            "run",
            "--dataset",
            str(dataset),
            "--out",
            str(output),
            "--provider",
            "mock",
            "--judge-provider",
            "mock",
            "--samples",
            "3",
        ]
    )

    assert exit_code == 0
    summary = (output / "summary.csv").read_text(encoding="utf-8")
    assert "baseline_generation" in summary
    assert "oracle_generation" in summary
    assert "human_reference" in summary
    assert "oracle_spec" in summary

    evaluations = list(output.rglob("evaluation.json"))
    assert len(evaluations) == 7
    payload = json.loads(evaluations[0].read_text(encoding="utf-8"))
    assert "sample_index" in payload
    assert payload["pytest"]["passed"] is True
    assert payload["pytest"]["sandbox"].startswith("docker:")

    stress_code = main(
        [
            "stress",
            "--run-dir",
            str(output),
            "--provider",
            "mock",
            "--pytest-timeout",
            "10",
            "--context-ablation",
        ]
    )

    assert stress_code == 0
    summary = (output / "summary.csv").read_text(encoding="utf-8")
    assert "stress_passed" in summary
    assert "maintenance_token_overhead" in summary
    assert "maintenance_failure_type" in summary
    stress_payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in output.rglob("stress.json")
    ]
    assert len(stress_payloads) == 7
    assert all(payload["pass_at_1"] for payload in stress_payloads)
    assert all(payload["context_ablation_pass_at_1"] for payload in stress_payloads)
    assert all(payload["maintenance_failure_type"] == "none" for payload in stress_payloads)
    assert all("maintenance_token_overhead" in payload for payload in stress_payloads)

    assert main(
        [
            "validate",
            "--run-dir",
            str(output),
            "--dataset",
            str(dataset),
            "--samples",
            "3",
            "--context-ablation",
        ]
    ) == 0

    benchmark_code = main(
        [
            "sandbox",
            "benchmark",
            "--iterations",
            "1",
            "--pytest-timeout",
            "10",
        ]
    )
    assert benchmark_code == 0


def test_cli_dataset_only_validate_rejects_bad_dataset(tmp_path: Path) -> None:
    dataset = tmp_path / "bad_dataset"
    dataset.mkdir()
    (dataset / "task.yaml").write_text(
        """
id: broken
entry_point: broken
prompt: |
  Implement broken().
test_code: |
  def test_placeholder():
      assert True
day2_prompt: |
  Extend broken().
day2_test_code: |
  def test_placeholder():
      assert True
day2_stressors: [not_in_design_notes]
human_reference: |
  def broken():
      return None
mock_solution: |
  def broken():
      return None
mock_day2_solution: |
  def broken():
      return None
""".lstrip(),
        encoding="utf-8",
    )

    assert main(["validate", "--dataset", str(dataset)]) == 1


def test_cli_generate_with_oracle_skill(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    output = tmp_path / "run"
    skill = tmp_path / "SKILL.md"
    dataset.mkdir()
    (dataset / "task.yaml").write_text(
        """
id: answer
entry_point: answer
prompt: |
  Implement answer() -> int returning 42.
test_code: |
  from solution import answer

  def test_answer():
      assert answer() == 42
day2_prompt: |
  Add answer_text() -> str returning "42".
day2_test_code: |
  def test_placeholder():
      assert True
day2_stressors: [interface_generalization]
human_reference: |
  def answer():
      return 42
mock_solution: |
  def answer():
      return 42
mock_day2_solution: |
  def answer():
      return 42
""".lstrip(),
        encoding="utf-8",
    )
    skill.write_text(
        """---
name: strict-simple
description: Use for simple oracle generation.
---

Prefer one small obvious implementation.
""",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "generate",
            "--dataset",
            str(dataset),
            "--out",
            str(output),
            "--provider",
            "mock",
            "--modes",
            "oracle",
            "--oracle-skill",
            str(skill),
        ]
    )

    assert exit_code == 0
    generation_path = next(output.rglob("generation.json"))
    payload = json.loads(generation_path.read_text(encoding="utf-8"))
    assert payload["oracle_spec_label"] == "custom_spec_override"
    assert payload["oracle_spec"] == "Prefer one small obvious implementation."
