import csv
import io
from typing import Dict, List, Tuple


def _parse_int(value: str) -> int:
    return int(value)


def aggregate_sales(csv_text: str) -> list[dict]:
    required_fields = ("region", "product", "quantity", "cents")
    totals: Dict[Tuple[str, str], List[int]] = {}

    reader = csv.DictReader(io.StringIO(csv_text, newline=""))

    if reader.fieldnames is None or any(field not in reader.fieldnames for field in required_fields):
        return []

    for row in reader:
        if None in row:
            continue

        try:
            region = row["region"]
            product = row["product"]
            quantity_text = row["quantity"]
            cents_text = row["cents"]
        except KeyError:
            continue

        if (
            region is None
            or product is None
            or quantity_text is None
            or cents_text is None
            or region == ""
            or product == ""
            or quantity_text == ""
            or cents_text == ""
        ):
            continue

        try:
            quantity = _parse_int(quantity_text)
            cents = _parse_int(cents_text)
        except ValueError:
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
