#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from math import comb
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable

import yaml

try:
    from scipy.stats import wilcoxon
except ImportError as exc:  # pragma: no cover - exercised only in broken envs.
    raise SystemExit(
        "scripts/analyze.py requires scipy. Install with: python3 -m pip install -e ."
    ) from exc


VARIANT_LABELS = {
    "baseline_generation": "Vibecoded Baseline",
    "oracle_generation": "In-Context Oracle",
    "neutral_style_generation": "Neutral Style",
    "human_reference": "Human Reference",
}
VARIANT_ORDER = (
    "baseline_generation",
    "neutral_style_generation",
    "oracle_generation",
    "human_reference",
)
NEAR_ZERO_STD_THRESHOLD = 0.05


@dataclass(frozen=True)
class TaskMeta:
    task_id: str
    tags: tuple[str, ...]
    day2_stressors: tuple[str, ...]


@dataclass(frozen=True)
class AggregateStats:
    variant: str
    label: str
    tasks: int
    samples: int
    pytest_pass_rate: float | None
    stress_pass_at_1: float | None
    stress_pass_at_3: float | None
    context_ablation_pass_at_1: float | None
    cc_average: float | None
    max_nesting_depth: float | None
    function_count: float | None
    maintenance_token_overhead: float | None
    maintainability_index: float | None
    judge_score: float | None


@dataclass(frozen=True)
class PairedTaskStats:
    task_id: str
    baseline_cc: float | None
    oracle_cc: float | None
    cc_delta: float | None
    baseline_nesting: float | None
    oracle_nesting: float | None
    nesting_delta: float | None
    baseline_functions: float | None
    oracle_functions: float | None
    function_delta: float | None
    baseline_stress: float | None
    oracle_stress: float | None
    baseline_context: float | None
    oracle_context: float | None
    inter_sample_cc_std: float | None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = load_summary_rows([Path(path) for path in args.summary])
    task_meta = load_task_meta(Path(args.dataset)) if args.dataset else {}

    markdown = render_report(rows, task_meta=task_meta, latex=False)
    latex = render_report(rows, task_meta=task_meta, latex=True)

    if args.markdown_out:
        Path(args.markdown_out).write_text(markdown + "\n", encoding="utf-8")
    if args.latex_out:
        Path(args.latex_out).write_text(latex + "\n", encoding="utf-8")

    if not args.markdown_out and not args.latex_out:
        print(markdown)
        print()
        print("```latex")
        print(latex)
        print("```")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate paper-ready SpecOracle tables from summary.csv files."
    )
    parser.add_argument("summary", nargs="+", help="one or more SpecOracle summary.csv files")
    parser.add_argument("--dataset", default=None, help="optional dataset for day2-hard subset analysis")
    parser.add_argument("--markdown-out", default=None, help="optional Markdown output path")
    parser.add_argument("--latex-out", default=None, help="optional LaTeX output path")
    return parser


def load_summary_rows(paths: Iterable[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            rows.extend(dict(row) for row in csv.DictReader(handle))
    return rows


def load_task_meta(path: Path) -> dict[str, TaskMeta]:
    payloads: list[dict] = []
    if path.is_file():
        payloads.extend(_load_task_file(path))
    else:
        for child in sorted(path.iterdir()):
            if child.suffix.lower() in {".yaml", ".yml", ".json"}:
                payloads.extend(_load_task_file(child))
    return {
        str(payload["id"]): TaskMeta(
            task_id=str(payload["id"]),
            tags=tuple(str(tag) for tag in payload.get("tags", ())),
            day2_stressors=tuple(str(item) for item in payload.get("day2_stressors", ())),
        )
        for payload in payloads
    }


def render_report(
    rows: list[dict[str, str]],
    *,
    task_meta: dict[str, TaskMeta],
    latex: bool,
) -> str:
    sections: list[str] = []
    sections.append(_section("Headline Metrics", latex=latex))
    sections.append(_render_aggregate_table(summarize_rows(rows), latex=latex, supplementary=False))
    sections.append(_render_wilcoxon(rows, latex=latex))
    sections.append(_render_variance_warning(rows, latex=latex))
    sections.append(_section("Measurement Validity", latex=latex))
    sections.append(_render_context_table(summarize_rows(rows), latex=latex))
    sections.append(_section("Supplementary Metrics", latex=latex))
    sections.append(_render_aggregate_table(summarize_rows(rows), latex=latex, supplementary=True))
    sections.append(_section("Per-Task Paired Breakdown", latex=latex))
    sections.append(_render_paired_table(paired_task_stats(rows), latex=latex))

    if task_meta:
        hard_task_ids = {
            task_id for task_id, meta in task_meta.items() if "day2-hard" in meta.tags
        }
        hard_rows = [row for row in rows if row.get("task_id") in hard_task_ids]
        sections.append(_section("Day 2 Hard Subset", latex=latex))
        sections.append(_render_aggregate_table(summarize_rows(hard_rows), latex=latex, supplementary=False))
        sections.append(_render_wilcoxon(hard_rows, latex=latex))

    return "\n\n".join(section for section in sections if section)


def summarize_rows(rows: Iterable[dict[str, str]]) -> list[AggregateStats]:
    row_list = list(rows)
    by_variant: dict[str, list[dict[str, str]]] = {variant: [] for variant in VARIANT_ORDER}
    for row in row_list:
        variant = row.get("variant", "")
        if variant in by_variant:
            by_variant[variant].append(row)

    stats = []
    for variant in VARIANT_ORDER:
        variant_rows = by_variant[variant]
        if not variant_rows:
            continue
        task_ids = {row.get("task_id", "") for row in variant_rows if row.get("task_id")}
        stats.append(
            AggregateStats(
                variant=variant,
                label=VARIANT_LABELS[variant],
                tasks=len(task_ids),
                samples=_max_samples_per_task(variant_rows),
                pytest_pass_rate=_rate(variant_rows, "pytest_passed"),
                stress_pass_at_1=_rate(variant_rows, "stress_passed"),
                stress_pass_at_3=_mean_pass_at_k(variant_rows, "stress_passed", 3),
                context_ablation_pass_at_1=_rate(variant_rows, "context_ablation_pass_at_1"),
                cc_average=_mean(variant_rows, "cc_average"),
                max_nesting_depth=_mean(variant_rows, "max_nesting_depth"),
                function_count=_mean(variant_rows, "function_count"),
                maintenance_token_overhead=_mean(variant_rows, "maintenance_token_overhead"),
                maintainability_index=_mean(variant_rows, "maintainability_index"),
                judge_score=_mean(variant_rows, "judge_score"),
            )
        )
    return stats


def paired_task_stats(rows: Iterable[dict[str, str]]) -> list[PairedTaskStats]:
    row_list = list(rows)
    task_ids = sorted({row.get("task_id", "") for row in row_list if row.get("task_id")})
    result = []
    for task_id in task_ids:
        baseline = [row for row in row_list if row.get("task_id") == task_id and row.get("variant") == "baseline_generation"]
        oracle = [row for row in row_list if row.get("task_id") == task_id and row.get("variant") == "oracle_generation"]
        if not baseline or not oracle:
            continue
        baseline_cc = _mean(baseline, "cc_average")
        oracle_cc = _mean(oracle, "cc_average")
        baseline_nesting = _mean(baseline, "max_nesting_depth")
        oracle_nesting = _mean(oracle, "max_nesting_depth")
        baseline_functions = _mean(baseline, "function_count")
        oracle_functions = _mean(oracle, "function_count")
        result.append(
            PairedTaskStats(
                task_id=task_id,
                baseline_cc=baseline_cc,
                oracle_cc=oracle_cc,
                cc_delta=_delta(oracle_cc, baseline_cc),
                baseline_nesting=baseline_nesting,
                oracle_nesting=oracle_nesting,
                nesting_delta=_delta(oracle_nesting, baseline_nesting),
                baseline_functions=baseline_functions,
                oracle_functions=oracle_functions,
                function_delta=_delta(oracle_functions, baseline_functions),
                baseline_stress=_rate(baseline, "stress_passed"),
                oracle_stress=_rate(oracle, "stress_passed"),
                baseline_context=_rate(baseline, "context_ablation_pass_at_1"),
                oracle_context=_rate(oracle, "context_ablation_pass_at_1"),
                inter_sample_cc_std=_combined_std(
                    _floats(baseline, "cc_average") + _floats(oracle, "cc_average")
                ),
            )
        )
    return result


def pass_at_k(n: int, c: int, k: int) -> float:
    if n <= 0:
        return 0.0
    if n < k:
        return float(c > 0)
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def wilcoxon_cc_pvalue(rows: Iterable[dict[str, str]]) -> float | None:
    pairs = paired_task_stats(rows)
    baseline = [pair.baseline_cc for pair in pairs if pair.baseline_cc is not None and pair.oracle_cc is not None]
    oracle = [pair.oracle_cc for pair in pairs if pair.baseline_cc is not None and pair.oracle_cc is not None]
    if len(baseline) < 2 or all(left == right for left, right in zip(baseline, oracle)):
        return None
    return float(wilcoxon(baseline, oracle, zero_method="wilcox", alternative="two-sided").pvalue)


def _render_aggregate_table(
    stats: list[AggregateStats],
    *,
    latex: bool,
    supplementary: bool,
) -> str:
    if supplementary:
        headers = ["Variant", "Tasks", "Samples", "MI", "Judge"]
        rows = [
            [
                item.label,
                str(item.tasks),
                str(item.samples),
                _format_float(item.maintainability_index),
                _format_float(item.judge_score),
            ]
            for item in stats
        ]
    else:
        headers = [
            "Variant",
            "Tasks",
            "Samples",
            "Pytest",
            "Maint. P@1",
            "Maint. P@3",
            "Context P@1",
            "CC Avg",
            "Nesting",
            "Functions",
            "Tokens",
        ]
        rows = [
            [
                item.label,
                str(item.tasks),
                str(item.samples),
                _format_rate(item.pytest_pass_rate, latex=latex),
                _format_rate(item.stress_pass_at_1, latex=latex),
                _format_rate(item.stress_pass_at_3, latex=latex),
                _format_rate(item.context_ablation_pass_at_1, latex=latex),
                _format_float(item.cc_average),
                _format_float(item.max_nesting_depth),
                _format_float(item.function_count),
                _format_float(item.maintenance_token_overhead),
            ]
            for item in stats
        ]
    return _table(headers, rows, latex=latex, label="tab:specoracle-comparison")


def _render_context_table(stats: list[AggregateStats], *, latex: bool) -> str:
    headers = ["Variant", "Real Context P@1", "Stub Context P@1", "Delta"]
    rows = []
    for item in stats:
        delta = _delta(item.stress_pass_at_1, item.context_ablation_pass_at_1)
        rows.append(
            [
                item.label,
                _format_rate(item.stress_pass_at_1, latex=latex),
                _format_rate(item.context_ablation_pass_at_1, latex=latex),
                _format_rate(delta, latex=latex, signed=True),
            ]
        )
    return _table(headers, rows, latex=latex, label="tab:specoracle-context-ablation")


def _render_paired_table(pairs: list[PairedTaskStats], *, latex: bool) -> str:
    headers = [
        "Task",
        "Base CC",
        "Oracle CC",
        "Delta",
        "Base Stress",
        "Oracle Stress",
        "Context Std",
    ]
    rows = [
        [
            pair.task_id,
            _format_float(pair.baseline_cc),
            _format_float(pair.oracle_cc),
            _format_float(pair.cc_delta, signed=True),
            _format_rate(pair.baseline_stress, latex=latex),
            _format_rate(pair.oracle_stress, latex=latex),
            _format_float(pair.inter_sample_cc_std),
        ]
        for pair in pairs
    ]
    return _table(headers, rows, latex=latex, label="tab:specoracle-paired")


def _render_wilcoxon(rows: list[dict[str, str]], *, latex: bool) -> str:
    pvalue = wilcoxon_cc_pvalue(rows)
    pairs = paired_task_stats(rows)
    deltas = [pair.cc_delta for pair in pairs if pair.cc_delta is not None]
    mean_delta = mean(deltas) if deltas else None
    wins = sum(1 for delta in deltas if delta < 0)
    losses = sum(1 for delta in deltas if delta > 0)
    ties = sum(1 for delta in deltas if delta == 0)
    text = (
        f"Paired CC delta oracle-baseline: mean={_format_float(mean_delta, signed=True)}, "
        f"oracle lower={wins}, oracle higher={losses}, ties={ties}, "
        f"Wilcoxon p={_format_float(pvalue)}."
    )
    return text if not latex else _latex_escape(text)


def _render_variance_warning(rows: list[dict[str, str]], *, latex: bool) -> str:
    pairs = paired_task_stats(rows)
    values = [
        pair.inter_sample_cc_std
        for pair in pairs
        if pair.inter_sample_cc_std is not None
    ]
    if not values:
        return ""
    low = sum(value < NEAR_ZERO_STD_THRESHOLD for value in values)
    text = (
        f"Inter-sample CC variance check: {low}/{len(values)} paired tasks have "
        f"std < {NEAR_ZERO_STD_THRESHOLD}."
    )
    return text if not latex else _latex_escape(text)


def _table(
    headers: list[str],
    rows: list[list[str]],
    *,
    latex: bool,
    label: str,
) -> str:
    if latex:
        alignment = "l" + "r" * (len(headers) - 1)
        lines = [
            "\\begin{table}[t]",
            "\\centering",
            f"\\label{{{label}}}",
            f"\\begin{{tabular}}{{{alignment}}}",
            "\\hline",
            " & ".join(_latex_escape(item) for item in headers) + " \\\\",
            "\\hline",
        ]
        lines.extend(" & ".join(_latex_escape(item) for item in row) + " \\\\" for row in rows)
        lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
        return "\n".join(lines)

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" if index == 0 else "---:" for index, _ in enumerate(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def _section(title: str, *, latex: bool) -> str:
    return f"\\paragraph{{{_latex_escape(title)}}}" if latex else f"## {title}"


def _load_task_file(path: Path) -> list[dict]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    return [dict(payload)]


def _mean(rows: list[dict[str, str]], field: str) -> float | None:
    values = _floats(rows, field)
    return mean(values) if values else None


def _rate(rows: list[dict[str, str]], field: str) -> float | None:
    values = [_as_bool(row.get(field, "")) for row in rows]
    present = [value for value in values if value is not None]
    return sum(1 for value in present if value) / len(present) if present else None


def _mean_pass_at_k(rows: list[dict[str, str]], field: str, k: int) -> float | None:
    by_task: dict[str, list[bool]] = {}
    for row in rows:
        parsed = _as_bool(row.get(field, ""))
        if parsed is not None:
            by_task.setdefault(row.get("task_id", ""), []).append(parsed)
    values = [
        pass_at_k(n=len(results), c=sum(1 for item in results if item), k=k)
        for results in by_task.values()
        if results
    ]
    return mean(values) if values else None


def _floats(rows: list[dict[str, str]], field: str) -> list[float]:
    values = [_as_float(row.get(field, "")) for row in rows]
    return [value for value in values if value is not None]


def _as_float(value: str) -> float | None:
    if value in {"", "None", "none", "null"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _as_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    return None


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def _combined_std(values: list[float]) -> float | None:
    return stdev(values) if len(values) >= 2 else None


def _max_samples_per_task(rows: list[dict[str, str]]) -> int:
    by_task: dict[str, set[int]] = {}
    for row in rows:
        by_task.setdefault(row.get("task_id", ""), set()).add(int(row.get("sample_index") or 0))
    return max((len(samples) for samples in by_task.values()), default=0)


def _format_rate(value: float | None, *, latex: bool = False, signed: bool = False) -> str:
    if value is None:
        return "--"
    prefix = "+" if signed and value > 0 else ""
    suffix = "\\%" if latex else "%"
    return f"{prefix}{value * 100:.1f}{suffix}"


def _format_float(value: float | None, *, signed: bool = False) -> str:
    if value is None:
        return "--"
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value:.3f}"


def _latex_escape(value: str) -> str:
    replacements = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
    }
    return "".join(replacements.get(char, char) for char in value)


if __name__ == "__main__":
    raise SystemExit(main())
