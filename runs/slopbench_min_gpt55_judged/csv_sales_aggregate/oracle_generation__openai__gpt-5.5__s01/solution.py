import csv
import io
from collections import defaultdict
from typing import DefaultDict

_REQUIRED_FIELDS = ("region", "product", "quantity", "cents")


def _parse_integer(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _has_required_headers(fieldnames: list[str] | None) -> bool:
    if fieldnames is None:
        return False
    return all(field in fieldnames for field in _REQUIRED_FIELDS)


def _is_complete_row(row: dict[str | None, str | None]) -> bool:
    if None in row:
        return False
    return all(row.get(field) is not None for field in _REQUIRED_FIELDS)


def aggregate_sales(csv_text: str) -> list[dict]:
    if not isinstance(csv_text, str):
        raise TypeError("csv_text must be a string")

    reader = csv.DictReader(io.StringIO(csv_text))

    if not _has_required_headers(reader.fieldnames):
        return []

    totals: DefaultDict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])

    for row in reader:
        if not _is_complete_row(row):
            continue

        quantity = _parse_integer(row["quantity"])
        cents = _parse_integer(row["cents"])
        if quantity is None or cents is None:
            continue

        key = (row["region"], row["product"])
        totals[key][0] += quantity
        totals[key][1] += cents

    return [
        {
            "region": region,
            "product": product,
            "quantity": quantity,
            "cents": cents,
        }
        for (region, product), (quantity, cents) in sorted(totals.items())
    ]
