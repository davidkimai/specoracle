import csv
import io
from typing import Optional


_REQUIRED_FIELDS = ("region", "product", "quantity", "cents")


def aggregate_sales(csv_text: str) -> list[dict]:
    if not isinstance(csv_text, str):
        raise TypeError("csv_text must be a string")

    reader = csv.DictReader(io.StringIO(csv_text, newline=""))

    if reader.fieldnames is None:
        return []

    if not _has_required_headers(reader.fieldnames):
        return []

    totals: dict[tuple[str, str], tuple[int, int]] = {}

    for row in reader:
        parsed = _parse_sales_row(row)
        if parsed is None:
            continue

        region, product, quantity, cents = parsed
        key = (region, product)
        current_quantity, current_cents = totals.get(key, (0, 0))
        totals[key] = (current_quantity + quantity, current_cents + cents)

    return [
        {
            "region": region,
            "product": product,
            "quantity": quantity,
            "cents": cents,
        }
        for (region, product), (quantity, cents) in sorted(totals.items())
    ]


def _has_required_headers(headers: list[str]) -> bool:
    return all(field in headers for field in _REQUIRED_FIELDS)


def _parse_sales_row(row: dict) -> Optional[tuple[str, str, int, int]]:
    if None in row:
        return None

    if not _has_required_values(row):
        return None

    quantity = _parse_int(row["quantity"])
    cents = _parse_int(row["cents"])

    if quantity is None or cents is None:
        return None

    return row["region"], row["product"], quantity, cents


def _has_required_values(row: dict) -> bool:
    for field in _REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or value == "":
            return False
    return True


def _parse_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None
