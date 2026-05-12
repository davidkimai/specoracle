import csv
import io
from collections import defaultdict


def aggregate_sales(csv_text: str) -> list[dict]:
    """
    Parse CSV text with headers region, product, quantity, cents.
    Skip malformed rows, missing fields, and rows with non-integer quantity or cents.
    Group by (region, product), summing quantity and cents.
    Return rows sorted by region then product.
    """
    required_fields = {"region", "product", "quantity", "cents"}
    totals = defaultdict(lambda: {"quantity": 0, "cents": 0})

    try:
        reader = csv.DictReader(io.StringIO(csv_text))
    except Exception:
        return []

    # Check if headers are present
    if reader.fieldnames is None:
        return []

    # Normalize fieldnames to check required fields
    fieldnames_lower = {f.strip().lower() for f in reader.fieldnames if f is not None}
    if not required_fields.issubset(fieldnames_lower):
        return []

    for row in reader:
        try:
            # Extract and strip values
            region = row.get("region")
            product = row.get("product")
            quantity_str = row.get("quantity")
            cents_str = row.get("cents")

            # Check all required fields are present and not None
            if any(v is None for v in [region, product, quantity_str, cents_str]):
                continue

            region = region.strip()
            product = product.strip()
            quantity_str = quantity_str.strip()
            cents_str = cents_str.strip()

            # Skip empty strings
            if not region or not product or not quantity_str or not cents_str:
                continue

            # Parse integers
            quantity = int(quantity_str)
            cents = int(cents_str)

        except (ValueError, TypeError, AttributeError):
            continue

        key = (region, product)
        totals[key]["quantity"] += quantity
        totals[key]["cents"] += cents

    result = [
        {
            "region": region,
            "product": product,
            "quantity": data["quantity"],
            "cents": data["cents"],
        }
        for (region, product), data in totals.items()
    ]

    result.sort(key=lambda r: (r["region"], r["product"]))
    return result
