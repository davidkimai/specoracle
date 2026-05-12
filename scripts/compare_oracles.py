#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Zen and Karpathy oracle sources.")
    parser.add_argument("--zen-run", default="runs/slopbench_full_claude")
    parser.add_argument("--karpathy-run", default="runs/karpathy_full_claude")
    parser.add_argument("--markdown-out", default="runs/oracle_source_comparison.md")
    parser.add_argument("--csv-out", default="runs/oracle_source_comparison.csv")
    args = parser.parse_args()

    rows = [
        summarize_cell(
            oracle_source="Zen of Python",
            run_dir=Path(args.zen_run),
            oracle_variant="oracle_generation",
        ),
        summarize_cell(
            oracle_source="Karpathy Guidelines",
            run_dir=Path(args.karpathy_run),
            oracle_variant="oracle_karpathy_generation",
        ),
    ]
    write_csv(rows, Path(args.csv_out))
    write_markdown(rows, Path(args.markdown_out))
    print(Path(args.markdown_out).resolve())
    print(Path(args.csv_out).resolve())
    return 0


def summarize_cell(
    *,
    oracle_source: str,
    run_dir: Path,
    oracle_variant: str,
    baseline_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    rows = read_summary(run_dir)
    baseline = baseline_rows or [row for row in rows if row.get("variant") == "baseline_generation"]
    oracle = [row for row in rows if row.get("variant") == oracle_variant]
    if not baseline:
        raise ValueError(f"{run_dir}: no baseline_generation rows")
    if not oracle:
        raise ValueError(f"{run_dir}: no {oracle_variant} rows")

    baseline_cc = mean_float(baseline, "cc_average")
    oracle_cc = mean_float(oracle, "cc_average")
    delta = oracle_cc - baseline_cc
    delta_pct = (delta / baseline_cc * 100.0) if baseline_cc else 0.0
    return {
        "oracle_source": oracle_source,
        "run_dir": str(run_dir),
        "model": model_label(oracle),
        "n": len({row["task_id"] for row in oracle}),
        "cc_base": baseline_cc,
        "cc_oracle": oracle_cc,
        "cc_delta": delta,
        "cc_delta_pct": delta_pct,
        "pass_at_1_base": pass_rate(baseline),
        "pass_at_1_oracle": pass_rate(oracle),
        "judge_score_oracle": mean_judge(oracle),
    }


def read_summary(run_dir: Path) -> list[dict[str, str]]:
    path = run_dir / "summary.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "oracle_source",
        "run_dir",
        "model",
        "n",
        "cc_base",
        "cc_oracle",
        "cc_delta",
        "cc_delta_pct",
        "pass_at_1_base",
        "pass_at_1_oracle",
        "judge_score_oracle",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Oracle Source Independence - Claude 4.6, Full SlopBench (50 tasks x 3 samples)",
        "",
        "Comparative evaluation of two independent oracle sources on Claude 4.6 (T=0.8).",
        "Zen of Python data from Sprint 1; Karpathy Guidelines from Sprint 3.",
        "",
        "| Oracle Source | N | CC (Base) | CC (Oracle) | Delta CC | Delta CC % | P@1 (Base) | P@1 (Oracle) | Judge |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {oracle_source} | {n} | {base} | {oracle} | {delta} | {delta_pct} | "
            "{base_pass} | {oracle_pass} | {judge} |".format(
                oracle_source=row["oracle_source"],
                n=row["n"],
                base=fmt(row["cc_base"]),
                oracle=fmt(row["cc_oracle"]),
                delta=fmt(row["cc_delta"]),
                delta_pct=fmt_pct(row["cc_delta_pct"]),
                base_pass=fmt_pct(row["pass_at_1_base"]),
                oracle_pass=fmt_pct(row["pass_at_1_oracle"]),
                judge=fmt(row["judge_score_oracle"]),
            )
        )
    lines.extend(
        [
            "",
            "Zen oracle: PEP 20 (https://peps.python.org/pep-0020/)",
            "Karpathy oracle: https://github.com/forrestchang/andrej-karpathy-skills",
            "Pipeline: https://github.com/davidkimai/specoracle",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def model_label(rows: list[dict[str, str]]) -> str:
    first = rows[0]
    return f"{first.get('provider', '')}/{first.get('model', '')}"


def mean_float(rows: list[dict[str, str]], field: str) -> float:
    values = [float(row[field]) for row in rows if row.get(field) not in {None, ""}]
    if not values:
        raise ValueError(f"no numeric values for {field}")
    return round(mean(values), 3)


def mean_judge(rows: list[dict[str, str]]) -> float | None:
    values = [
        float(row["judge_score"])
        for row in rows
        if row.get("judge_score") not in {None, ""} and str(row.get("judge_skipped")).lower() != "true"
    ]
    return round(mean(values), 3) if values else None


def pass_rate(rows: list[dict[str, str]]) -> float:
    values = [row.get("pytest_passed") for row in rows if row.get("pytest_passed") not in {None, ""}]
    if not values:
        raise ValueError("no pytest_passed values")
    passed = sum(1 for value in values if str(value).lower() == "true")
    return round(passed / len(values) * 100.0, 1)


def fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def fmt_pct(value: float | None) -> str:
    return "" if value is None else f"{value:.1f}%"


if __name__ == "__main__":
    raise SystemExit(main())
