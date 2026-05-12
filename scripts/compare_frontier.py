#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from statistics import mean
from typing import Any


HARD_VARIANTS = (
    "modular_discovery_generation",
    "oracle_dafny_generation",
    "dafny_generation",
    "hard_oracle_generation",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate baseline, soft-oracle, and hard-oracle frontier evidence."
    )
    parser.add_argument("--baseline-run", default="runs/slopbench_full_claude")
    parser.add_argument("--karpathy-run", default="runs/karpathy_full_claude")
    parser.add_argument("--dafny-run", default=None)
    parser.add_argument("--require-dafny", action="store_true")
    parser.add_argument("--markdown-out", default="runs/pareto_frontier_analysis.md")
    parser.add_argument("--csv-out", default="runs/pareto_frontier_analysis.csv")
    args = parser.parse_args()

    rows = [
        summarize_run(
            label="Baseline",
            run_dir=Path(args.baseline_run),
            variants=("baseline_generation",),
            required=True,
        ),
        summarize_run(
            label="Karpathy soft oracle",
            run_dir=Path(args.karpathy_run),
            variants=("oracle_karpathy_generation",),
            required=True,
        ),
    ]
    rows.append(
        summarize_run(
            label="Dafny modular hard oracle",
            run_dir=Path(args.dafny_run) if args.dafny_run else None,
            variants=HARD_VARIANTS,
            required=bool(args.require_dafny),
        )
    )

    write_csv(rows, Path(args.csv_out))
    write_markdown(rows, Path(args.markdown_out))
    print(Path(args.markdown_out).resolve())
    print(Path(args.csv_out).resolve())
    return 0


def summarize_run(
    *,
    label: str,
    run_dir: Path | None,
    variants: tuple[str, ...],
    required: bool,
) -> dict[str, Any]:
    if run_dir is None:
        if required:
            raise FileNotFoundError(f"{label}: required run directory was not provided")
        return missing_row(label, "not_provided")

    summary_path = run_dir / "summary.csv"
    if not summary_path.exists():
        if required:
            raise FileNotFoundError(f"{label}: required summary.csv missing at {summary_path}")
        return missing_row(label, f"missing {summary_path}")

    with summary_path.open(newline="", encoding="utf-8") as handle:
        summary_rows = list(csv.DictReader(handle))
    rows = [row for row in summary_rows if row.get("variant") in variants]
    if not rows:
        if required:
            expected = ", ".join(variants)
            raise ValueError(f"{label}: no rows found for required variant(s): {expected}")
        return missing_row(label, f"no rows for {', '.join(variants)}")

    variant = rows[0].get("variant", "")
    return {
        "oracle": label,
        "run_dir": str(run_dir),
        "variant": variant,
        "n_tasks": len({row.get("task_id", "") for row in rows if row.get("task_id")}),
        "samples": len(rows),
        "pass_at_1": rate(rows, "pytest_passed"),
        "dafny_status": dafny_status(rows, run_dir=run_dir, variants=variants),
        "avg_cc": mean_float(rows, "cc_average"),
        "avg_nesting": mean_float(rows, "max_nesting_depth"),
        "compiled_bloat_token_ratio": compiled_bloat_ratio(
            rows,
            run_dir=run_dir,
            variants=variants,
        ),
        "note": "",
    }


def missing_row(label: str, note: str) -> dict[str, Any]:
    return {
        "oracle": label,
        "run_dir": "",
        "variant": "",
        "n_tasks": "",
        "samples": "",
        "pass_at_1": None,
        "dafny_status": "missing",
        "avg_cc": None,
        "avg_nesting": None,
        "compiled_bloat_token_ratio": None,
        "note": note,
    }


def dafny_status(rows: list[dict[str, str]], *, run_dir: Path, variants: tuple[str, ...]) -> str:
    status_values = [
        row.get("dafny_status", "")
        for row in rows
        if row.get("dafny_status") not in {None, ""}
    ]
    verified_values = [
        row.get("dafny_verified", "")
        for row in rows
        if row.get("dafny_verified") not in {None, ""}
    ]
    artifact_values = artifact_dafny_values(run_dir, variants)
    if artifact_values:
        verified = sum(1 for value in artifact_values if truthy(value))
        return f"verified {verified}/{len(artifact_values)}"
    if verified_values:
        verified = sum(1 for value in verified_values if truthy(value))
        return f"verified {verified}/{len(verified_values)}"
    if status_values:
        return "; ".join(sorted(set(status_values)))
    return "not_available"


def artifact_dafny_values(run_dir: Path, variants: tuple[str, ...]) -> list[Any]:
    values: list[Any] = []
    for path in sorted(run_dir.rglob("*.json")):
        if path.name not in {"generation.json", "evaluation.json"}:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("variant") not in variants:
            continue
        for container_key in ("dafny", "metadata"):
            container = payload.get(container_key)
            if not isinstance(container, dict):
                continue
            if "verified" in container:
                values.append(container["verified"])
            nested = container.get("dafny")
            if isinstance(nested, dict) and "verified" in nested:
                values.append(nested["verified"])
    return values


def compiled_bloat_ratio(
    rows: list[dict[str, str]],
    *,
    run_dir: Path,
    variants: tuple[str, ...],
) -> float | None:
    summary_values = [
        float(row["compiled_bloat_token_ratio"])
        for row in rows
        if row.get("compiled_bloat_token_ratio") not in {None, ""}
    ]
    if summary_values:
        return round(mean(summary_values), 3)

    ratios: list[float] = []
    for generation_path in sorted(run_dir.rglob("generation.json")):
        payload = json.loads(generation_path.read_text(encoding="utf-8"))
        if payload.get("variant") not in variants:
            continue
        artifact_dir = generation_path.parent
        direct = payload.get("code")
        solution_path = artifact_dir / "solution.py"
        if not direct and solution_path.exists():
            direct = solution_path.read_text(encoding="utf-8")
        compiled = compiled_python_for_artifact(artifact_dir, payload)
        if direct and compiled:
            direct_tokens = token_count(str(direct))
            compiled_tokens = token_count(compiled)
            if direct_tokens:
                ratios.append(compiled_tokens / direct_tokens)
    return round(mean(ratios), 3) if ratios else None


def compiled_python_for_artifact(artifact_dir: Path, payload: dict[str, Any]) -> str | None:
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        for key in ("compiled_python", "compiled_python_code"):
            if isinstance(metadata.get(key), str):
                return str(metadata[key])
        nested = metadata.get("dafny")
        if isinstance(nested, dict):
            for key in ("compiled_python", "compiled_python_code"):
                if isinstance(nested.get(key), str):
                    return str(nested[key])

    for name in ("compiled_solution.py", "compiled.py", "dafny_compiled.py"):
        path = artifact_dir / name
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "oracle",
        "run_dir",
        "variant",
        "n_tasks",
        "samples",
        "pass_at_1",
        "dafny_status",
        "avg_cc",
        "avg_nesting",
        "compiled_bloat_token_ratio",
        "note",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Verification-Slop Pareto Frontier",
        "",
        "| Oracle | N | Samples | Pass@1 | Dafny | Avg CC | Avg Nesting | Bloat Ratio | Note |",
        "|---|---:|---:|---:|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {oracle} | {n_tasks} | {samples} | {pass_at_1} | {dafny_status} | "
            "{avg_cc} | {avg_nesting} | {bloat} | {note} |".format(
                oracle=row["oracle"],
                n_tasks=row["n_tasks"],
                samples=row["samples"],
                pass_at_1=fmt_pct(row["pass_at_1"]),
                dafny_status=row["dafny_status"],
                avg_cc=fmt_float(row["avg_cc"]),
                avg_nesting=fmt_float(row["avg_nesting"]),
                bloat=fmt_float(row["compiled_bloat_token_ratio"]),
                note=row["note"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def mean_float(rows: list[dict[str, str]], field: str) -> float | None:
    values = [float(row[field]) for row in rows if row.get(field) not in {None, ""}]
    return round(mean(values), 3) if values else None


def rate(rows: list[dict[str, str]], field: str) -> float | None:
    values = [row.get(field) for row in rows if row.get(field) not in {None, ""}]
    if not values:
        return None
    return round(sum(1 for value in values if truthy(value)) / len(values) * 100.0, 1)


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "passed", "verified"}


def token_count(text: str) -> int:
    return len(re.findall(r"\w+|[^\s\w]", text))


def fmt_float(value: Any) -> str:
    return "" if value in {None, ""} else f"{float(value):.3f}"


def fmt_pct(value: Any) -> str:
    return "" if value in {None, ""} else f"{float(value):.1f}%"


if __name__ == "__main__":
    raise SystemExit(main())
