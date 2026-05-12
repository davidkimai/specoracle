import csv
import io
from collections import defaultdict
from typing import Dict, List, Tuple

_REQUIRED_FIELDS = ("region", "product", "quantity", "cents")


def _parse_decimal_integer(value: str) -> int:
    text = value.strip()
    if not text:
        raise ValueError("empty integer field")

    start = 1 if text[0] in "+-" else 0
    if start == len(text) or not text[start:].isdigit():
        raise ValueError("not a decimal integer")

    return int(text, 10)


def aggregate_sales(csv_text: str) -> list[dict]:
    totals: Dict[Tuple[str, str], List[int]] = defaultdict(lambda: [0, 0])

    try:
        reader = csv.DictReader(io.StringIO(csv_text), restkey=None, restval=None, strict=True)
        fieldnames = reader.fieldnames
    except csv.Error:
        return []

    if fieldnames is None or any(field not in fieldnames for field in _REQUIRED_FIELDS):
        return []

    try:
        for row in reader:
            if None in row:
                continue

            region = row.get("region")
            product = row.get("product")
            quantity_text = row.get("quantity")
            cents_text = row.get("cents")

            if (
                region is None
                or product is None
                or quantity_text is None
                or cents_text is None
            ):
                continue

            try:
                quantity = _parse_decimal_integer(quantity_text)
                cents = _parse_decimal_integer(cents_text)
            except ValueError:
                continue

            aggregate = totals[(region, product)]
            aggregate[0] += quantity
            aggregate[1] += cents
    except csv.Error:
        pass

    return [
        {
            "region": region,
            "product": product,
            "quantity": values[0],
            "cents": values[1],
        }
        for (region, product), values in sorted(totals.items(), key=lambda item: item[0])
    ]
