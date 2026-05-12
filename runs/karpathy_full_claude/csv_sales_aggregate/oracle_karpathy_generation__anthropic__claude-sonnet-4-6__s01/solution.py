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

        key = (region, product)
        totals[key][0] += quantity
        totals[key][1] += cents

    return [
        {"region": r, "product": p, "quantity": q, "cents": c}
        for (r, p), (q, c) in sorted(totals.items())
    ]
