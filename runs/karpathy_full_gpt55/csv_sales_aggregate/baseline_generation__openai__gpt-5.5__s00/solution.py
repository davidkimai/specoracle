import csv
import io
from typing import Dict, List, Tuple


_REQUIRED_FIELDS = ("region", "product", "quantity", "cents")
_EXTRA_FIELDS_KEY = "__extra_fields__"


def _parse_integer(value: str) -> int | None:
    text = value.strip()
    if not text:
        return None

    if text[0] in "+-":
        digits = text[1:]
        if not digits:
            return None
    else:
        digits = text

    if not digits.isdigit():
        return None

    return int(text)


def aggregate_sales(csv_text: str) -> list[dict]:
    totals: Dict[Tuple[str, str], List[int]] = {}

    stream = io.StringIO(csv_text)
    try:
        reader = csv.DictReader(stream, restkey=_EXTRA_FIELDS_KEY, restval=None)
    except csv.Error:
        return []

    if reader.fieldnames is None:
        return []

    fieldnames = list(reader.fieldnames)
    if fieldnames:
        fieldnames[0] = fieldnames[0].removeprefix("\ufeff")

    if any(field not in fieldnames for field in _REQUIRED_FIELDS):
        return []

    try:
        for row in reader:
            if _EXTRA_FIELDS_KEY in row:
                continue

            if any(field not in row or row[field] is None for field in _REQUIRED_FIELDS):
                continue

            region = row["region"]
            product = row["product"]
            quantity = _parse_integer(row["quantity"])
            cents = _parse_integer(row["cents"])

            if quantity is None or cents is None:
                continue

            key = (region, product)
            if key not in totals:
                totals[key] = [0, 0]
            totals[key][0] += quantity
            totals[key][1] += cents
    except csv.Error:
        pass

    return [
        {
            "region": region,
            "product": product,
            "quantity": values[0],
            "cents": values[1],
        }
        for (region, product), values in sorted(totals.items())
    ]
