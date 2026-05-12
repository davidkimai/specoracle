import csv
import io
from typing import Dict, List, Tuple


def aggregate_sales(csv_text: str) -> list[dict]:
    required_fields = ("region", "product", "quantity", "cents")
    totals: Dict[Tuple[str, str], Dict[str, int]] = {}

    try:
        reader = csv.DictReader(io.StringIO(csv_text), skipinitialspace=True)
    except csv.Error:
        return []

    if not reader.fieldnames or any(field not in reader.fieldnames for field in required_fields):
        return []

    try:
        for row in reader:
            if row is None:
                continue

            if None in row:
                continue

            if any(row.get(field) is None for field in required_fields):
                continue

            region = row["region"]
            product = row["product"]

            try:
                quantity = int(row["quantity"])
                cents = int(row["cents"])
            except (TypeError, ValueError):
                continue

            key = (region, product)
            if key not in totals:
                totals[key] = {"quantity": 0, "cents": 0}

            totals[key]["quantity"] += quantity
            totals[key]["cents"] += cents
    except csv.Error:
        return []

    return [
        {
            "region": region,
            "product": product,
            "quantity": totals[(region, product)]["quantity"],
            "cents": totals[(region, product)]["cents"],
        }
        for region, product in sorted(totals)
    ]
