import csv
import subprocess
import sys
from pathlib import Path


def test_compare_providers_outputs_markdown_and_csv(tmp_path: Path) -> None:
    run_a = tmp_path / "run_a"
    run_b = tmp_path / "run_b"
    run_a.mkdir()
    run_b.mkdir()
    _write_summary(run_a / "summary.csv", provider="anthropic", model="claude-sonnet-4-6")
    _write_summary(run_b / "summary.csv", provider="google", model="gemini-2.5-pro")
    markdown_out = tmp_path / "comparison.md"
    csv_out = tmp_path / "comparison.csv"

    subprocess.run(
        [
            sys.executable,
            "scripts/compare_providers.py",
            str(run_a),
            str(run_b),
            "--markdown-out",
            str(markdown_out),
            "--csv-out",
            str(csv_out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    markdown = markdown_out.read_text(encoding="utf-8")
    assert "anthropic/claude-sonnet-4-6" in markdown
    assert "google/gemini-2.5-pro" in markdown
    rows = list(csv.DictReader(csv_out.open(newline="", encoding="utf-8")))
    assert len(rows) == 2
    assert rows[0]["cc_delta_pct"]


def _write_summary(path: Path, *, provider: str, model: str) -> None:
    fields = [
        "task_id",
        "variant",
        "provider",
        "model",
        "sample_index",
        "cc_average",
        "pytest_passed",
        "judge_score",
    ]
    rows = [
        {
            "task_id": "answer",
            "variant": "baseline_generation",
            "provider": provider,
            "model": model,
            "sample_index": "0",
            "cc_average": "10",
            "pytest_passed": "True",
            "judge_score": "7",
        },
        {
            "task_id": "answer",
            "variant": "oracle_generation",
            "provider": provider,
            "model": model,
            "sample_index": "0",
            "cc_average": "5",
            "pytest_passed": "True",
            "judge_score": "9",
        },
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
