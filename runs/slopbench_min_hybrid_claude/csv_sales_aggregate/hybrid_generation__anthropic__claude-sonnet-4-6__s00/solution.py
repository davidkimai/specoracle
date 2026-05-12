import csv
import io
from collections import defaultdict


REQUIRED_FIELDS = {"region", "product", "quantity", "cents"}


def _parse_int_fields(row):
    """Return (quantity, cents) as ints, or raise ValueError."""
    return int(row["quantity"]), int(row["cents"])


def _extract_key(row):
    """Return (region, product) stripped, or None if either is blank."""
    region = row["region"].strip()
    product = row["product"].strip()
    if not region or not product:
        return None
    return region, product


def _valid_headers(fieldnames):
    return fieldnames is not None and REQUIRED_FIELDS.issubset(fieldnames)


def _accumulate_row(row, totals):
    key = _extract_key(row)
    if key is None:
        return
    try:
        quantity, cents = _parse_int_fields(row)
    except (ValueError, TypeError):
        return
    totals[key]["quantity"] += quantity
    totals[key]["cents"] += cents


def aggregate_sales(csv_text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    if not _valid_headers(reader.fieldnames):
        return []

    totals = defaultdict(lambda: {"quantity": 0, "cents": 0})
    for row in reader:
        if REQUIRED_FIELDS.issubset(row):
            _accumulate_row(row, totals)

    return [
        {"region": region, "product": product, **sums}
        for (region, product), sums in sorted(totals.items())
    ]
