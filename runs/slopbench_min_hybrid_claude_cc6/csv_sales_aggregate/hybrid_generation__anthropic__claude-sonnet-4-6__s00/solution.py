import csv
import io
from collections import defaultdict


REQUIRED_FIELDS = {"region", "product", "quantity", "cents"}


def _parse_integers(row):
    """Return (quantity, cents) as ints, or raise ValueError."""
    return int(row["quantity"]), int(row["cents"])


def _has_required_fields(fieldnames):
    return fieldnames is not None and REQUIRED_FIELDS.issubset(set(fieldnames))


def _valid_row(row):
    return row.get("region") is not None and row.get("product") is not None


def _accumulate(totals, row):
    try:
        quantity, cents = _parse_integers(row)
    except (ValueError, TypeError):
        return
    key = (row["region"], row["product"])
    totals[key]["quantity"] += quantity
    totals[key]["cents"] += cents


def _build_result(totals):
    rows = [
        {"region": region, "product": product, "quantity": data["quantity"], "cents": data["cents"]}
        for (region, product), data in totals.items()
    ]
    rows.sort(key=lambda r: (r["region"], r["product"]))
    return rows


def aggregate_sales(csv_text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    if not _has_required_fields(reader.fieldnames):
        return []

    totals = defaultdict(lambda: {"quantity": 0, "cents": 0})
    for row in reader:
        if _valid_row(row):
            _accumulate(totals, row)

    return _build_result(totals)
