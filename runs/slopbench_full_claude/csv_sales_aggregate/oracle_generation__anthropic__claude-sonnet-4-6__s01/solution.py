"""
csv_sales_aggregate.py

Aggregates sales data from CSV text, grouping by (region, product)
and summing quantity and cents.
"""

import csv
import io
from collections import defaultdict

REQUIRED_FIELDS = {"region", "product", "quantity", "cents"}


def _parse_row(row: dict) -> tuple[str, str, int, int] | None:
    """
    Validate and parse a single CSV row.
    Returns (region, product, quantity, cents) or None if the row is malformed.
    """
    if not REQUIRED_FIELDS.issubset(row.keys()):
        return None

    region = row["region"].strip()
    product = row["product"].strip()

    if not region or not product:
        return None

    try:
        quantity = int(row["quantity"])
        cents = int(row["cents"])
    except (ValueError, TypeError):
        return None

    return region, product, quantity, cents


def aggregate_sales(csv_text: str) -> list[dict]:
    """
    Parse CSV text and aggregate sales by (region, product).

    Skips rows that are malformed, missing required fields, or have
    non-integer quantity or cents values.

    Returns a list of dicts sorted by region then product, each containing:
        {"region": str, "product": str, "quantity": int, "cents": int}
    """
    reader = csv.DictReader(io.StringIO(csv_text))

    totals: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"quantity": 0, "cents": 0}
    )

    for raw_row in reader:
        parsed = _parse_row(raw_row)
        if parsed is None:
            continue
        region, product, quantity, cents = parsed
        key = (region, product)
        totals[key]["quantity"] += quantity
        totals[key]["cents"] += cents

    result = [
        {"region": region, "product": product, **sums}
        for (region, product), sums in totals.items()
    ]

    result.sort(key=lambda row: (row["region"], row["product"]))
    return result
