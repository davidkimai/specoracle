import csv
import subprocess
import sys
from pathlib import Path


def test_compare_oracles_outputs_markdown_and_csv(tmp_path: Path) -> None:
    zen = tmp_path / "zen"
    karpathy = tmp_path / "karpathy"
    zen.mkdir()
    karpathy.mkdir()
    _write_summary(zen / "summary.csv", oracle_variant="oracle_generation", oracle_cc="6")
    _write_summary(
        karpathy / "summary.csv",
        oracle_variant="oracle_karpathy_generation",
        oracle_cc="5",
    )
    markdown = tmp_path / "oracle.md"
    csv_out = tmp_path / "oracle.csv"

    subprocess.run(
        [
            sys.executable,
            "scripts/compare_oracles.py",
            "--zen-run",
            str(zen),
            "--karpathy-run",
            str(karpathy),
            "--markdown-out",
            str(markdown),
            "--csv-out",
            str(csv_out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = markdown.read_text(encoding="utf-8")
    assert "Zen of Python" in text
    assert "Karpathy Guidelines" in text
    rows = list(csv.DictReader(csv_out.open(newline="", encoding="utf-8")))
    assert len(rows) == 2
    assert rows[1]["cc_delta_pct"]


def test_compare_factorial_outputs_all_six_cells(tmp_path: Path) -> None:
    zen_claude = tmp_path / "zen_claude"
    karpathy_claude = tmp_path / "karpathy_claude"
    karpathy_gpt = tmp_path / "karpathy_gpt"
    karpathy_gemini = tmp_path / "karpathy_gemini"
    zen_gpt = tmp_path / "zen_gpt"
    zen_gemini = tmp_path / "zen_gemini"
    for path in [
        zen_claude,
        karpathy_claude,
        karpathy_gpt,
        karpathy_gemini,
        zen_gpt,
        zen_gemini,
    ]:
        path.mkdir()
    _write_summary(zen_claude / "summary.csv", oracle_variant="oracle_generation", oracle_cc="6")
    _write_summary(
        karpathy_claude / "summary.csv",
        oracle_variant="oracle_karpathy_generation",
        oracle_cc="5",
    )
    _write_summary(
        karpathy_gpt / "summary.csv",
        oracle_variant="oracle_karpathy_generation",
        oracle_cc="4",
        provider="openai",
        model="gpt-5.5",
    )
    _write_summary(
        karpathy_gemini / "summary.csv",
        oracle_variant="oracle_karpathy_generation",
        oracle_cc="7",
        provider="google",
        model="gemini-2.5-pro",
    )
    _write_summary(
        zen_gpt / "summary.csv",
        oracle_variant="oracle_generation",
        oracle_cc="6",
        provider="openai",
        model="gpt-5.5",
        include_baseline=False,
    )
    _write_summary(
        zen_gemini / "summary.csv",
        oracle_variant="oracle_generation",
        oracle_cc="6",
        provider="google",
        model="gemini-2.5-pro",
        include_baseline=False,
    )
    markdown = tmp_path / "factorial.md"
    csv_out = tmp_path / "factorial.csv"

    subprocess.run(
        [
            sys.executable,
            "scripts/compare_factorial.py",
            "--zen-claude",
            str(zen_claude),
            "--karpathy-claude",
            str(karpathy_claude),
            "--karpathy-gpt",
            str(karpathy_gpt),
            "--karpathy-gemini",
            str(karpathy_gemini),
            "--zen-gpt",
            str(zen_gpt),
            "--zen-gemini",
            str(zen_gemini),
            "--markdown-out",
            str(markdown),
            "--csv-out",
            str(csv_out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = markdown.read_text(encoding="utf-8")
    assert "Oracle x Model Factorial Comparison" in text
    rows = list(csv.DictReader(csv_out.open(newline="", encoding="utf-8")))
    assert len(rows) == 6
    assert {row["oracle"] for row in rows} == {"Zen", "Karpathy"}


def _write_summary(
    path: Path,
    *,
    oracle_variant: str,
    oracle_cc: str,
    provider: str = "anthropic",
    model: str = "claude-sonnet-4-6",
    include_baseline: bool = True,
) -> None:
    fields = [
        "task_id",
        "variant",
        "provider",
        "model",
        "sample_index",
        "cc_average",
        "pytest_passed",
        "judge_score",
        "judge_skipped",
    ]
    rows = []
    if include_baseline:
        rows.append(
            {
                "task_id": "answer",
                "variant": "baseline_generation",
                "provider": provider,
                "model": model,
                "sample_index": "0",
                "cc_average": "10",
                "pytest_passed": "True",
                "judge_score": "7",
                "judge_skipped": "False",
            }
        )
    rows.append(
        {
            "task_id": "answer",
            "variant": oracle_variant,
            "provider": provider,
            "model": model,
            "sample_index": "0",
            "cc_average": oracle_cc,
            "pytest_passed": "True",
            "judge_score": "9",
            "judge_skipped": "False",
        }
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
