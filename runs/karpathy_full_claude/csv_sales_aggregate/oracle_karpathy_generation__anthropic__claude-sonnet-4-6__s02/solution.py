import csv
import io
from collections import defaultdict


def aggregate_sales(csv_text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    totals = defaultdict(lambda: [0, 0])

    for row in reader:
        try:
            region = row["region"]
            product = row["product"]
            quantity = int(row["quantity"])
            cents = int(row["cents"])
        except (KeyError, TypeError, ValueError):
            continue

        totals[(region, product)][0] += quantity
        totals[(region, product)][1] += cents

    result = [
        {"region": k[0], "product": k[1], "quantity": v[0], "cents": v[1]}
        for k, v in sorted(totals.items())
    ]
    return result
