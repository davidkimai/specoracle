import csv
from io import StringIO
from typing import Dict, List, Tuple


_REQUIRED_FIELDS = ("region", "product", "quantity", "cents")


def _has_required_headers(fieldnames: list[str] | None) -> bool:
    if fieldnames is None:
        return False
    return all(field in fieldnames for field in _REQUIRED_FIELDS)


def _row_has_required_values(row: dict) -> bool:
    if None in row:
        return False
    return all(row.get(field) not in (None, "") for field in _REQUIRED_FIELDS)


def _parse_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def aggregate_sales(csv_text: str) -> List[Dict[str, object]]:
    if not isinstance(csv_text, str):
        raise TypeError("csv_text must be a string")

    reader = csv.DictReader(StringIO(csv_text))

    if not _has_required_headers(reader.fieldnames):
        return []

    totals: dict[Tuple[str, str], tuple[int, int]] = {}

    for row in reader:
        if not _row_has_required_values(row):
            continue

        quantity = _parse_int(row["quantity"])
        cents = _parse_int(row["cents"])

        if quantity is None or cents is None:
            continue

        key = (row["region"], row["product"])
        old_quantity, old_cents = totals.get(key, (0, 0))
        totals[key] = (old_quantity + quantity, old_cents + cents)

    return [
        {
            "region": region,
            "product": product,
            "quantity": quantity,
            "cents": cents,
        }
        for (region, product), (quantity, cents) in sorted(totals.items())
    ]
