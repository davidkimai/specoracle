from __future__ import annotations

import csv
import io
from collections import defaultdict
from typing import DefaultDict


REQUIRED_HEADERS = ("region", "product", "quantity", "cents")


def aggregate_sales(csv_text: str) -> list[dict]:
    if not isinstance(csv_text, str):
        raise TypeError("csv_text must be a string")

    reader = csv.DictReader(io.StringIO(csv_text))
    _validate_headers(reader.fieldnames)

    totals: DefaultDict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"quantity": 0, "cents": 0}
    )

    for row in reader:
        parsed = _parse_row(row)
        if parsed is None:
            continue

        region, product, quantity, cents = parsed
        key = (region, product)
        totals[key]["quantity"] += quantity
        totals[key]["cents"] += cents

    return _format_totals(totals)


def _validate_headers(fieldnames: list[str] | None) -> None:
    if fieldnames is None:
        raise ValueError("CSV input must include a header row")

    missing = [name for name in REQUIRED_HEADERS if name not in fieldnames]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"CSV header is missing required field(s): {joined}")


def _parse_row(row: dict[str | None, str | list[str] | None]) -> tuple[str, str, int, int] | None:
    if None in row:
        return None

    values = [row.get(name) for name in REQUIRED_HEADERS]
    if any(value is None for value in values):
        return None

    region = values[0]
    product = values[1]
    quantity_text = values[2]
    cents_text = values[3]

    if not isinstance(region, str) or not isinstance(product, str):
        return None
    if not isinstance(quantity_text, str) or not isinstance(cents_text, str):
        return None

    quantity = _parse_int(quantity_text)
    cents = _parse_int(cents_text)
    if quantity is None or cents is None:
        return None

    return region, product, quantity, cents


def _parse_int(text: str) -> int | None:
    try:
        return int(text)
    except ValueError:
        return None


def _format_totals(totals: dict[tuple[str, str], dict[str, int]]) -> list[dict]:
    rows = []
    for region, product in sorted(totals):
        values = totals[(region, product)]
        rows.append(
            {
                "region": region,
                "product": product,
                "quantity": values["quantity"],
                "cents": values["cents"],
            }
        )
    return rows
