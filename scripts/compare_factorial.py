#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean
from typing import Any

from compare_oracles import fmt, fmt_pct, read_summary, summarize_cell


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare oracle source by model factorial results.")
    parser.add_argument("--zen-claude", default="runs/slopbench_full_claude")
    parser.add_argument("--karpathy-claude", default="runs/karpathy_full_claude")
    parser.add_argument("--karpathy-gpt", default="runs/karpathy_full_gpt55")
    parser.add_argument("--karpathy-gemini", default="runs/karpathy_full_gemini")
    parser.add_argument("--zen-gpt", default="runs/zen_full_gpt55")
    parser.add_argument("--zen-gemini", default="runs/zen_full_gemini")
    parser.add_argument("--markdown-out", default="runs/factorial_comparison.md")
    parser.add_argument("--csv-out", default="runs/factorial_comparison.csv")
    args = parser.parse_args()

    rows = build_rows(args)
    write_csv(rows, Path(args.csv_out))
    write_markdown(rows, Path(args.markdown_out))
    print(Path(args.markdown_out).resolve())
    print(Path(args.csv_out).resolve())
    return 0


def build_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    karpathy_gpt_rows = read_summary(Path(args.karpathy_gpt))
    karpathy_gemini_rows = read_summary(Path(args.karpathy_gemini))
    gpt_baseline = [row for row in karpathy_gpt_rows if row.get("variant") == "baseline_generation"]
    gemini_baseline = [row for row in karpathy_gemini_rows if row.get("variant") == "baseline_generation"]

    rows = [
        with_labels(
            summarize_cell(
                oracle_source="Zen of Python",
                run_dir=Path(args.zen_claude),
                oracle_variant="oracle_generation",
            ),
            oracle="Zen",
            model="Claude 4.6",
        ),
        with_labels(
            summarize_cell(
                oracle_source="Zen of Python",
                run_dir=Path(args.zen_gpt),
                oracle_variant="oracle_generation",
                baseline_rows=gpt_baseline,
            ),
            oracle="Zen",
            model="GPT-5.5",
        ),
        with_labels(
            summarize_cell(
                oracle_source="Zen of Python",
                run_dir=Path(args.zen_gemini),
                oracle_variant="oracle_generation",
                baseline_rows=gemini_baseline,
            ),
            oracle="Zen",
            model="Gemini 2.5 Pro",
        ),
        with_labels(
            summarize_cell(
                oracle_source="Karpathy Guidelines",
                run_dir=Path(args.karpathy_claude),
                oracle_variant="oracle_karpathy_generation",
            ),
            oracle="Karpathy",
            model="Claude 4.6",
        ),
        with_labels(
            summarize_cell(
                oracle_source="Karpathy Guidelines",
                run_dir=Path(args.karpathy_gpt),
                oracle_variant="oracle_karpathy_generation",
            ),
            oracle="Karpathy",
            model="GPT-5.5",
        ),
        with_labels(
            summarize_cell(
                oracle_source="Karpathy Guidelines",
                run_dir=Path(args.karpathy_gemini),
                oracle_variant="oracle_karpathy_generation",
            ),
            oracle="Karpathy",
            model="Gemini 2.5 Pro",
        ),
    ]
    return rows


def with_labels(row: dict[str, Any], *, oracle: str, model: str) -> dict[str, Any]:
    row = dict(row)
    row["oracle"] = oracle
    row["display_model"] = model
    return row


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "oracle",
        "display_model",
        "model",
        "n",
        "cc_base",
        "cc_oracle",
        "cc_delta",
        "cc_delta_pct",
        "pass_at_1_base",
        "pass_at_1_oracle",
        "judge_score_oracle",
        "run_dir",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    models = ["Claude 4.6", "GPT-5.5", "Gemini 2.5 Pro"]
    oracles = ["Zen", "Karpathy"]
    by_cell = {(row["oracle"], row["display_model"]): row for row in rows}

    lines = [
        "# Oracle x Model Factorial Comparison - Full SlopBench (50 tasks x 3 samples)",
        "",
        "Two oracle sources x three frontier models. Each cell shows mean CC delta (%) "
        "relative to that model's baseline.",
        "",
        "| Oracle Source | Claude 4.6 | GPT-5.5 | Gemini 2.5 Pro | Mean |",
        "|---|---:|---:|---:|---:|",
    ]
    for oracle in oracles:
        values = [by_cell[(oracle, model)]["cc_delta_pct"] for model in models]
        lines.append(
            "| {oracle} | {claude} | {gpt} | {gemini} | {avg} |".format(
                oracle="Zen of Python" if oracle == "Zen" else "Karpathy Guidelines",
                claude=fmt_pct(values[0]),
                gpt=fmt_pct(values[1]),
                gemini=fmt_pct(values[2]),
                avg=fmt_pct(round(mean(values), 3)),
            )
        )
    model_means = [
        round(mean(by_cell[(oracle, model)]["cc_delta_pct"] for oracle in oracles), 3)
        for model in models
    ]
    all_mean = round(mean(row["cc_delta_pct"] for row in rows), 3)
    lines.extend(
        [
            "| **Model Mean** | **{claude}** | **{gpt}** | **{gemini}** | **{avg}** |".format(
                claude=fmt_pct(model_means[0]),
                gpt=fmt_pct(model_means[1]),
                gemini=fmt_pct(model_means[2]),
                avg=fmt_pct(all_mean),
            ),
            "",
            "## Detailed Metrics",
            "",
            "| Oracle | Model | N | CC (Base) | CC (Oracle) | Delta CC | Delta % | P@1 (B) | P@1 (O) | Judge |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| {oracle} | {model} | {n} | {base} | {oracle_cc} | {delta} | {delta_pct} | "
            "{base_pass} | {oracle_pass} | {judge} |".format(
                oracle=row["oracle"],
                model=row["display_model"],
                n=row["n"],
                base=fmt(row["cc_base"]),
                oracle_cc=fmt(row["cc_oracle"]),
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


if __name__ == "__main__":
    raise SystemExit(main())
