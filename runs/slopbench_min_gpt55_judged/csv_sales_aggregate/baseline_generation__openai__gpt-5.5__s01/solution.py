import csv
import io
from collections import defaultdict
from typing import Dict, List, Tuple


_REQUIRED_FIELDS = ("region", "product", "quantity", "cents")


def _to_int(value: str) -> int:
    value = value.strip()
    if value == "":
        raise ValueError("empty integer field")
    return int(value, 10)


def aggregate_sales(csv_text: str) -> list[dict]:
    totals: Dict[Tuple[str, str], List[int]] = defaultdict(lambda: [0, 0])

    stream = io.StringIO(csv_text)

    try:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
    except csv.Error:
        return []

    if not fieldnames or any(field not in fieldnames for field in _REQUIRED_FIELDS):
        return []

    try:
        for row in reader:
            if row is None:
                continue

            if None in row:
                continue

            if any(row.get(field) is None for field in _REQUIRED_FIELDS):
                continue

            region = row["region"]
            product = row["product"]

            try:
                quantity = _to_int(row["quantity"])
                cents = _to_int(row["cents"])
            except (ValueError, TypeError):
                continue

            key = (region, product)
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
        for (region, product), values in sorted(totals.items(), key=lambda item: item[0])
    ]
