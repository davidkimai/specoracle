import csv
import io
from typing import Dict, List, Tuple


def _parse_int(value: str) -> int:
    if value is None:
        raise ValueError("missing integer field")
    return int(value)


def aggregate_sales(csv_text: str) -> list[dict]:
    required_fields = {"region", "product", "quantity", "cents"}
    totals: Dict[Tuple[str, str], List[int]] = {}

    try:
        reader = csv.DictReader(io.StringIO(csv_text), strict=True)
    except csv.Error:
        return []

    if reader.fieldnames is None or not required_fields.issubset(set(reader.fieldnames)):
        return []

    while True:
        try:
            row = next(reader)
        except StopIteration:
            break
        except csv.Error:
            continue

        if row is None:
            continue

        if None in row:
            continue

        try:
            region = row["region"]
            product = row["product"]
            quantity_raw = row["quantity"]
            cents_raw = row["cents"]
        except KeyError:
            continue

        if region is None or product is None or quantity_raw is None or cents_raw is None:
            continue

        try:
            quantity = _parse_int(quantity_raw)
            cents = _parse_int(cents_raw)
        except (TypeError, ValueError):
            continue

        key = (region, product)
        if key not in totals:
            totals[key] = [0, 0]
        totals[key][0] += quantity
        totals[key][1] += cents

    return [
        {
            "region": region,
            "product": product,
            "quantity": values[0],
            "cents": values[1],
        }
        for (region, product), values in sorted(totals.items(), key=lambda item: item[0])
    ]
