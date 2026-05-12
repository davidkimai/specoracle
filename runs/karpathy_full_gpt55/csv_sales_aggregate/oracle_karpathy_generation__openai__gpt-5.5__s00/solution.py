import csv
import io


def aggregate_sales(csv_text: str) -> list[dict]:
    """Aggregate valid CSV sales rows by (region, product)."""
    totals = {}

    reader = csv.DictReader(io.StringIO(csv_text), strict=True)
    required = ("region", "product", "quantity", "cents")

    if reader.fieldnames is None or any(name not in reader.fieldnames for name in required):
        return []

    while True:
        try:
            row = next(reader)
        except StopIteration:
            break
        except csv.Error:
            continue

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
