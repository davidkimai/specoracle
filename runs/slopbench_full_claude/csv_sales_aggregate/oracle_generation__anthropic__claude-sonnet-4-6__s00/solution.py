"""
csv_sales_aggregate.py

Aggregate sales data from CSV text, grouping by (region, product).
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
    Parse CSV text and return aggregated sales grouped by (region, product).

    Skips malformed rows, rows with missing fields, and rows where quantity
    or cents are not integers.

    Returns a list of dicts sorted by region then product, each with keys:
    region, product, quantity, cents.
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
        totals[(region, product)]["quantity"] += quantity
        totals[(region, product)]["cents"] += cents

    return [
        {
            "region": region,
            "product": product,
            "quantity": sums["quantity"],
            "cents": sums["cents"],
        }
        for (region, product), sums in sorted(totals.items())
    ]
