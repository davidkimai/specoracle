import csv
import io
from collections import defaultdict


def aggregate_sales(csv_text: str, *, min_quantity: int = 0) -> list[dict]:
    """
    Parse CSV text with headers region, product, quantity, cents.
    Skip malformed rows, missing fields, and rows with non-integer quantity or cents.
    Group by (region, product), summing quantity and cents.
    Return rows sorted by region then product.
    Omit groups whose final aggregate quantity is less than min_quantity.
    """
    required_fields = {"region", "product", "quantity", "cents"}
    aggregated = defaultdict(lambda: {"quantity": 0, "cents": 0})

    try:
        reader = csv.DictReader(io.StringIO(csv_text))
    except Exception:
        return []

    # Check if headers are present
    if reader.fieldnames is None:
        # Try to read to trigger fieldname population
        try:
            first_row = next(iter(reader), None)
            if reader.fieldnames is None:
                return []
        except Exception:
            return []

    for row in reader:
        # Skip rows where required fields are missing or None
        if not required_fields.issubset(row.keys()):
            continue

        region = row.get("region")
        product = row.get("product")
        quantity_str = row.get("quantity")
        cents_str = row.get("cents")

        # Skip if any required value is None or empty
        if region is None or product is None or quantity_str is None or cents_str is None:
            continue

        region = region.strip()
        product = product.strip()
        quantity_str = quantity_str.strip()
        cents_str = cents_str.strip()

        if not region or not product:
            continue

        # Validate integer fields
        try:
            quantity = int(quantity_str)
            cents = int(cents_str)
        except (ValueError, TypeError):
            continue

        key = (region, product)
        aggregated[key]["quantity"] += quantity
        aggregated[key]["cents"] += cents

    result = [
        {
            "region": region,
            "product": product,
            "quantity": data["quantity"],
            "cents": data["cents"],
        }
        for (region, product), data in aggregated.items()
        if data["quantity"] >= min_quantity
    ]

    result.sort(key=lambda x: (x["region"], x["product"]))
    return result
