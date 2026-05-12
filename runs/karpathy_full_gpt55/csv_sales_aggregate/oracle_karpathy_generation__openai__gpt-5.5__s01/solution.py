import csv
from io import StringIO


def aggregate_sales(csv_text: str) -> list[dict]:
    """Aggregate valid sales rows by (region, product)."""
    required = ("region", "product", "quantity", "cents")
    totals: dict[tuple[str, str], list[int]] = {}

    reader = csv.DictReader(StringIO(csv_text))
    if reader.fieldnames is None or any(name not in reader.fieldnames for name in required):
        return []

    for row in reader:
        if None in row:
            continue

        region = row.get("region")
        product = row.get("product")
        quantity_text = row.get("quantity")
        cents_text = row.get("cents")

        if None in (region, product, quantity_text, cents_text):
            continue

        try:
            quantity = int(quantity_text)
            cents = int(cents_text)
        except ValueError:
            continue

        key = (region, product)
        if key not in totals:
            totals[key] = [0, 0]
        totals[key][0] += quantity
        totals[key][1] += cents

    return [
        {"region": region, "product": product, "quantity": values[0], "cents": values[1]}
        for (region, product), values in sorted(totals.items())
    ]
