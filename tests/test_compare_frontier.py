import csv
import json
import subprocess
import sys
from pathlib import Path


def test_compare_frontier_outputs_optional_missing_dafny_row(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    karpathy = tmp_path / "karpathy"
    baseline.mkdir()
    karpathy.mkdir()
    _write_summary(baseline / "summary.csv", variant="baseline_generation", cc="9")
    _write_summary(karpathy / "summary.csv", variant="oracle_karpathy_generation", cc="5")
    markdown = tmp_path / "frontier.md"
    csv_out = tmp_path / "frontier.csv"

    subprocess.run(
        [
            sys.executable,
            "scripts/compare_frontier.py",
            "--baseline-run",
            str(baseline),
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
    rows = list(csv.DictReader(csv_out.open(newline="", encoding="utf-8")))
    assert "Verification-Slop Pareto Frontier" in text
    assert len(rows) == 3
    assert rows[2]["oracle"] == "Dafny modular hard oracle"
    assert rows[2]["dafny_status"] == "missing"


def test_compare_frontier_aggregates_hard_oracle_artifacts(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    karpathy = tmp_path / "karpathy"
    dafny = tmp_path / "dafny"
    artifact = dafny / "answer" / "modular_discovery_generation__mock__unit__s00"
    baseline.mkdir()
    karpathy.mkdir()
    artifact.mkdir(parents=True)
    _write_summary(baseline / "summary.csv", variant="baseline_generation", cc="9")
    _write_summary(karpathy / "summary.csv", variant="oracle_karpathy_generation", cc="5")
    _write_summary(
        dafny / "summary.csv",
        variant="modular_discovery_generation",
        cc="7",
        extra_fields=("dafny_verified",),
        extra_values={"dafny_verified": "True"},
    )
    (artifact / "solution.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    (artifact / "compiled_solution.py").write_text(
        "def answer():\n    value = 42\n    return value\n",
        encoding="utf-8",
    )
    (artifact / "generation.json").write_text(
        json.dumps(
            {
                "task_id": "answer",
                "variant": "modular_discovery_generation",
                "code": "def answer():\n    return 42\n",
                "metadata": {"dafny": {"verified": True}},
            }
        ),
        encoding="utf-8",
    )
    csv_out = tmp_path / "frontier.csv"

    subprocess.run(
        [
            sys.executable,
            "scripts/compare_frontier.py",
            "--baseline-run",
            str(baseline),
            "--karpathy-run",
            str(karpathy),
            "--dafny-run",
            str(dafny),
            "--markdown-out",
            str(tmp_path / "frontier.md"),
            "--csv-out",
            str(csv_out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = list(csv.DictReader(csv_out.open(newline="", encoding="utf-8")))
    hard = rows[2]
    assert hard["variant"] == "modular_discovery_generation"
    assert hard["dafny_status"] == "verified 1/1"
    assert hard["compiled_bloat_token_ratio"]


def test_compare_frontier_required_input_fails_clearly(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/compare_frontier.py",
            "--baseline-run",
            str(tmp_path / "missing"),
            "--karpathy-run",
            str(tmp_path / "also_missing"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "required summary.csv missing" in completed.stderr


def _write_summary(
    path: Path,
    *,
    variant: str,
    cc: str,
    extra_fields: tuple[str, ...] = (),
    extra_values: dict[str, str] | None = None,
) -> None:
    fields = [
        "task_id",
        "variant",
        "provider",
        "model",
        "sample_index",
        "cc_average",
        "max_nesting_depth",
        "pytest_passed",
        *extra_fields,
    ]
    row = {
        "task_id": "answer",
        "variant": variant,
        "provider": "mock",
        "model": "unit",
        "sample_index": "0",
        "cc_average": cc,
        "max_nesting_depth": "2",
        "pytest_passed": "True",
    }
    row.update(extra_values or {})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)
