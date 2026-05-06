import csv
import io
from collections import defaultdict


def aggregate_sales(csv_text: str, *, min_quantity: int = 0) -> list[dict]:
    """
    Parse CSV text with headers region, product, quantity, cents.
    Skip malformed rows, missing fields, and rows with non-integer quantity or cents.
    Group by (region, product), summing quantity and cents.
    Return rows sorted by region then product.

    min_quantity: omit groups whose final aggregate quantity is less than this value.
    """
    required_fields = {"region", "product", "quantity", "cents"}
    aggregated = defaultdict(lambda: {"quantity": 0, "cents": 0})

    try:
        reader = csv.DictReader(io.StringIO(csv_text))
    except Exception:
        return []

    # Check if headers exist
    if reader.fieldnames is None:
        return []

    # Normalize fieldnames to check required fields
    try:
        fieldnames_set = {f.strip() for f in reader.fieldnames if f is not None}
    except Exception:
        return []

    if not required_fields.issubset(fieldnames_set):
        return []

    for row in reader:
        try:
            # Check all required fields are present and not None
            if any(row.get(field) is None for field in required_fields):
                continue

            region = row["region"].strip()
            product = row["product"].strip()
            quantity_str = row["quantity"].strip()
            cents_str = row["cents"].strip()

            # Skip empty strings
            if not region or not product or not quantity_str or not cents_str:
                continue

            quantity = int(quantity_str)
            cents = int(cents_str)

        except (ValueError, AttributeError, KeyError):
            continue

        key = (region, product)
        aggregated[key]["quantity"] += quantity
        aggregated[key]["cents"] += cents

    result = []
    for (region, product), totals in aggregated.items():
        if totals["quantity"] < min_quantity:
            continue
        result.append({
            "region": region,
            "product": product,
            "quantity": totals["quantity"],
            "cents": totals["cents"],
        })

    result.sort(key=lambda r: (r["region"], r["product"]))
    return result
