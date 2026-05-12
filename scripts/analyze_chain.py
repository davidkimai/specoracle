#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


BANDS = (
    ("LOW", 0.0, 50_000.0),
    ("MED", 50_000.0, 150_000.0),
    ("HIGH", 150_000.0, float("inf")),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze chained SpecArena results.")
    parser.add_argument("path", help="chain_results.json, chain_summary.csv, or run directory")
    parser.add_argument("--markdown-out", default=None)
    args = parser.parse_args()

    rows = load_chain_rows(Path(args.path))
    report = build_report(rows)
    print(report)
    if args.markdown_out:
        Path(args.markdown_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown_out).write_text(report + "\n", encoding="utf-8")
    return 0


def load_chain_rows(path: Path) -> list[dict[str, Any]]:
    if path.is_dir():
        if (path / "chain_summary.csv").exists():
            path = path / "chain_summary.csv"
        else:
            path = path / "chain_results.json"
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("steps"), list):
        return [dict(row) for row in payload["steps"]]
    if isinstance(payload, list):
        return [dict(row) for row in payload]
    raise ValueError(f"unsupported chain results payload: {path}")


def build_report(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# SpecArena v2 Chain Analysis",
        "",
        "## Per-Step Differential",
        "",
        "| Step | Variant | Pass% | Avg CC | Avg Tokens | Accum Score |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for row in _step_rows(rows):
        lines.append(
            f"| {row['step']} | {row['variant']} | {_pct(row['pass_rate'])} | "
            f"{row['avg_cc']:.3f} | {row['avg_tokens']:.1f} | {row['avg_score']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Complexity Bands",
            "",
            "| Band | Score Range | N | Base Pass% | Oracle Pass% | Hybrid Pass% |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    band_rows = _band_rows(rows)
    for row in band_rows:
        lines.append(
            f"| {row['band']} | {row['range']} | {row['n']} | "
            f"{_pct(row.get('baseline_generation'))} | "
            f"{_pct(row.get('oracle_generation'))} | "
            f"{_pct(row.get('hybrid_generation'))} |"
        )

    threshold_found, threshold_band, finding = _verdict(band_rows)
    lines.extend(
        [
            "",
            f"THRESHOLD_FOUND: {threshold_found}",
            f"THRESHOLD_BAND: {threshold_band}",
            f'FINDING: "{finding}"',
        ]
    )
    return "\n".join(lines)


def _step_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["step"]), str(row["variant"]))].append(row)
    result: list[dict[str, Any]] = []
    for (step, variant), group in sorted(grouped.items()):
        result.append(
            {
                "step": step,
                "variant": variant,
                "pass_rate": _pass_rate(group),
                "avg_cc": _mean(group, "cc_average"),
                "avg_tokens": _mean(group, "token_estimate"),
                "avg_score": _mean(group, "accumulated_score"),
            }
        )
    return result


def _band_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for name, low, high in BANDS:
        in_band = [
            row
            for row in rows
            if low <= float(row.get("accumulated_score") or 0.0) < high
        ]
        band: dict[str, Any] = {
            "band": name,
            "range": _range_label(low, high),
            "n": len(in_band),
        }
        for variant in {"baseline_generation", "oracle_generation", "hybrid_generation"}:
            variant_rows = [row for row in in_band if row.get("variant") == variant]
            band[variant] = _pass_rate(variant_rows) if variant_rows else None
        result.append(band)
    return result


def _verdict(band_rows: list[dict[str, Any]]) -> tuple[bool, str, str]:
    for row in band_rows:
        baseline = row.get("baseline_generation")
        best_constrained = max(
            value
            for value in (row.get("oracle_generation"), row.get("hybrid_generation"))
            if value is not None
        ) if any(row.get(key) is not None for key in ("oracle_generation", "hybrid_generation")) else None
        if baseline is None or best_constrained is None:
            continue
        if best_constrained - baseline >= 10.0 and row["n"] > 0:
            return (
                True,
                str(row["band"]),
                (
                    f"At accumulated score {row['range']}, constrained variants exceed "
                    f"baseline pass rate by {best_constrained - baseline:.1f} points."
                ),
            )
    return (
        False,
        "INCONCLUSIVE",
        "No differential failure rate observed across complexity bands. Longer chains or higher-complexity tasks required.",
    )


def _pass_rate(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    passed = sum(1 for row in rows if str(row.get("pass_bool")).lower() == "true")
    return passed / len(rows) * 100.0


def _mean(rows: list[dict[str, Any]], field: str) -> float:
    values = [float(row.get(field) or 0.0) for row in rows]
    return mean(values) if values else 0.0


def _pct(value: float | None) -> str:
    return "" if value is None else f"{value:.1f}%"


def _range_label(low: float, high: float) -> str:
    if high == float("inf"):
        return f">{int(low / 1000)}K"
    if low == 0:
        return f"<{int(high / 1000)}K"
    return f"{int(low / 1000)}K-{int(high / 1000)}K"


if __name__ == "__main__":
    raise SystemExit(main())
