#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare SpecOracle run directories by provider/model.")
    parser.add_argument("run_dirs", nargs="+", help="run directories containing summary.csv")
    parser.add_argument("--markdown-out", default="runs/cross_model_comparison.md")
    parser.add_argument("--csv-out", default="runs/cross_model_comparison.csv")
    args = parser.parse_args()

    rows = compare_run_dirs([Path(item) for item in args.run_dirs])
    write_csv(rows, Path(args.csv_out))
    write_markdown(rows, Path(args.markdown_out))
    print(Path(args.markdown_out).resolve())
    print(Path(args.csv_out).resolve())
    return 0


def compare_run_dirs(run_dirs: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        summary_path = run_dir / "summary.csv"
        if not summary_path.exists():
            raise FileNotFoundError(summary_path)
        with summary_path.open(newline="", encoding="utf-8") as handle:
            summary_rows = list(csv.DictReader(handle))
        groups: dict[tuple[str, str], list[dict[str, str]]] = {}
        for row in summary_rows:
            variant = row.get("variant", "")
            if variant not in {"baseline_generation", "oracle_generation"}:
                continue
            key = (row.get("provider", ""), row.get("model", ""))
            groups.setdefault(key, []).append(row)
        for (provider, model), group in sorted(groups.items()):
            baseline = [row for row in group if row.get("variant") == "baseline_generation"]
            oracle = [row for row in group if row.get("variant") == "oracle_generation"]
            baseline_cc = _mean_float(baseline, "cc_average")
            oracle_cc = _mean_float(oracle, "cc_average")
            cc_delta_pct = (
                ((oracle_cc - baseline_cc) / baseline_cc * 100.0)
                if baseline_cc not in {None, 0}
                else None
            )
            rows.append(
                {
                    "run_dir": str(run_dir),
                    "model": f"{provider}/{model}",
                    "cc_avg_baseline": baseline_cc,
                    "cc_avg_oracle": oracle_cc,
                    "cc_delta_pct": cc_delta_pct,
                    "pass_at_1_baseline": _pass_rate(baseline),
                    "pass_at_1_oracle": _pass_rate(oracle),
                    "judge_score_oracle": _mean_float(oracle, "judge_score"),
                }
            )
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "run_dir",
        "model",
        "cc_avg_baseline",
        "cc_avg_oracle",
        "cc_delta_pct",
        "pass_at_1_baseline",
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
        "# Cross-Model SpecOracle Comparison",
        "",
        "| Model | CC Avg (Base) | CC Avg (Oracle) | CC Delta | Pass@1 (Base) | Pass@1 (Oracle) | Judge Score (Oracle) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {model} | {base_cc} | {oracle_cc} | {delta} | {base_pass} | {oracle_pass} | {judge} |".format(
                model=row["model"],
                base_cc=_fmt(row["cc_avg_baseline"]),
                oracle_cc=_fmt(row["cc_avg_oracle"]),
                delta=_fmt_pct(row["cc_delta_pct"]),
                base_pass=_fmt_pct(row["pass_at_1_baseline"]),
                oracle_pass=_fmt_pct(row["pass_at_1_oracle"]),
                judge=_fmt(row["judge_score_oracle"]),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mean_float(rows: list[dict[str, str]], field: str) -> float | None:
    values = [float(row[field]) for row in rows if row.get(field) not in {None, ""}]
    return round(mean(values), 3) if values else None


def _pass_rate(rows: list[dict[str, str]]) -> float | None:
    values = [row.get("pytest_passed") for row in rows if row.get("pytest_passed") not in {None, ""}]
    if not values:
        return None
    passed = sum(1 for value in values if str(value).lower() == "true")
    return round(passed / len(values) * 100.0, 1)


def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def _fmt_pct(value: float | None) -> str:
    return "" if value is None else f"{value:.1f}%"


if __name__ == "__main__":
    raise SystemExit(main())
