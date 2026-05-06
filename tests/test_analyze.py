import csv
import importlib.util
import sys
from pathlib import Path


def _load_analyze_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "analyze.py"
    spec = importlib.util.spec_from_file_location("specoracle_analyze", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_summary(path: Path) -> None:
    fieldnames = [
        "task_id",
        "variant",
        "sample_index",
        "pytest_passed",
        "stress_passed",
        "context_ablation_pass_at_1",
        "cc_average",
        "max_nesting_depth",
        "function_count",
        "maintainability_index",
        "judge_score",
        "maintenance_token_overhead",
    ]
    rows = []
    for task_id in ("a", "b"):
        rows.append(
            {
                "task_id": task_id,
                "variant": "human_reference",
                "sample_index": "0",
                "pytest_passed": "True",
                "stress_passed": "True",
                "context_ablation_pass_at_1": "True",
                "cc_average": "2",
                "max_nesting_depth": "1",
                "function_count": "1",
                "maintainability_index": "90",
                "judge_score": "9",
                "maintenance_token_overhead": "60",
            }
        )
        for sample in range(3):
            rows.append(
                {
                    "task_id": task_id,
                    "variant": "baseline_generation",
                    "sample_index": str(sample),
                    "pytest_passed": "True",
                    "stress_passed": "True" if sample < 2 else "False",
                    "context_ablation_pass_at_1": "False",
                    "cc_average": str(6 + sample),
                    "max_nesting_depth": "3",
                    "function_count": "1",
                    "maintainability_index": "80",
                    "judge_score": "7",
                    "maintenance_token_overhead": "100",
                }
            )
            rows.append(
                {
                    "task_id": task_id,
                    "variant": "oracle_generation",
                    "sample_index": str(sample),
                    "pytest_passed": "True",
                    "stress_passed": "True",
                    "context_ablation_pass_at_1": "True" if sample == 0 else "False",
                    "cc_average": str(3 + sample),
                    "max_nesting_depth": "1",
                    "function_count": "3",
                    "maintainability_index": "70",
                    "judge_score": "9",
                    "maintenance_token_overhead": "90",
                }
            )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_analyze_renders_headline_supplementary_and_paired_tables(tmp_path: Path) -> None:
    analyze = _load_analyze_module()
    summary = tmp_path / "summary.csv"
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    (dataset / "task.yaml").write_text(
        """
id: a
tags: [day2-hard]
day2_stressors: [interface_generalization]
""".lstrip(),
        encoding="utf-8",
    )
    _write_summary(summary)

    rows = analyze.load_summary_rows([summary])
    markdown = analyze.render_report(rows, task_meta=analyze.load_task_meta(dataset), latex=False)
    latex = analyze.render_report(rows, task_meta=analyze.load_task_meta(dataset), latex=True)

    assert "Maint. P@3" in markdown
    assert "Context P@1" in markdown
    assert "Supplementary Metrics" in markdown
    assert "Per-Task Paired Breakdown" in markdown
    assert "Wilcoxon p=" in markdown
    assert "\\begin{table}" in latex


def test_pass_at_k_uses_chen_estimator() -> None:
    analyze = _load_analyze_module()

    assert analyze.pass_at_k(3, 2, 3) == 1.0
    assert round(analyze.pass_at_k(3, 1, 2), 6) == round(2 / 3, 6)
    assert analyze.pass_at_k(2, 1, 3) == 1.0


def test_analyze_cli_writes_both_outputs(tmp_path: Path) -> None:
    analyze = _load_analyze_module()
    summary = tmp_path / "summary.csv"
    _write_summary(summary)
    markdown_out = tmp_path / "table.md"
    latex_out = tmp_path / "table.tex"

    assert analyze.main(
        [
            str(summary),
            "--markdown-out",
            str(markdown_out),
            "--latex-out",
            str(latex_out),
        ]
    ) == 0

    assert "In-Context Oracle" in markdown_out.read_text(encoding="utf-8")
    assert "\\begin{tabular}" in latex_out.read_text(encoding="utf-8")
