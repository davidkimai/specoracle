import csv
import io
from collections import defaultdict


def aggregate_sales(csv_text: str, *, min_quantity: int = 0) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    totals = defaultdict(lambda: {"quantity": 0, "cents": 0})

    for row in reader:
        if not _row_is_valid(row):
            continue
        key = (row["region"].strip(), row["product"].strip())
        quantity, cents = _parse_ints(row)
        totals[key]["quantity"] += quantity
        totals[key]["cents"] += cents

    return [
        {"region": region, "product": product, **sums}
        for (region, product), sums in sorted(totals.items())
        if sums["quantity"] >= min_quantity
    ]


def _row_is_valid(row: dict) -> bool:
    required = {"region", "product", "quantity", "cents"}
    if not required.issubset(row.keys()):
        return False
    if any(row[field] is None or str(row[field]).strip() == "" for field in required):
        return False
    return _parse_ints(row) is not None


def _parse_ints(row: dict) -> tuple[int, int] | None:
    try:
        quantity = int(str(row["quantity"]).strip())
        cents = int(str(row["cents"]).strip())
        return quantity, cents
    except (ValueError, KeyError):
        return None
