import csv
from io import StringIO


def aggregate_sales(csv_text: str) -> list[dict]:
    reader = csv.DictReader(StringIO(csv_text))
    required = ("region", "product", "quantity", "cents")

    if reader.fieldnames is None or any(name not in reader.fieldnames for name in required):
        return []

    totals = {}

    for row in reader:
        if None in row:
            continue

        region = row.get("region")
        product = row.get("product")
        quantity_text = row.get("quantity")
        cents_text = row.get("cents")

        if (
            region in (None, "")
            or product in (None, "")
            or quantity_text in (None, "")
            or cents_text in (None, "")
        ):
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
        {
            "region": region,
            "product": product,
            "quantity": quantity,
            "cents": cents,
        }
        for (region, product), (quantity, cents) in sorted(totals.items())
    ]
