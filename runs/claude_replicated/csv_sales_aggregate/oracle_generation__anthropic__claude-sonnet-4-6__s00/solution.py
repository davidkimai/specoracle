import csv
import io
from collections import defaultdict


def aggregate_sales(csv_text: str) -> list[dict]:
    """
    Parse CSV text with headers region, product, quantity, cents.
    Skip malformed rows. Group by (region, product), summing quantity and cents.
    Return rows sorted by region then product.
    """
    totals = defaultdict(lambda: {"quantity": 0, "cents": 0})

    reader = csv.DictReader(io.StringIO(csv_text))

    required_fields = {"region", "product", "quantity", "cents"}
    if reader.fieldnames is None or not required_fields.issubset(set(reader.fieldnames)):
        return []

    for row in reader:
        if not required_fields.issubset(row.keys()):
            continue

        region = row["region"]
        product = row["product"]

        if not region or not product:
            continue

        try:
            quantity = int(row["quantity"])
            cents = int(row["cents"])
        except (ValueError, TypeError):
            continue

        key = (region, product)
        totals[key]["quantity"] += quantity
        totals[key]["cents"] += cents

    result = [
        {"region": region, "product": product, "quantity": sums["quantity"], "cents": sums["cents"]}
        for (region, product), sums in totals.items()
    ]

    result.sort(key=lambda r: (r["region"], r["product"]))
    return result
