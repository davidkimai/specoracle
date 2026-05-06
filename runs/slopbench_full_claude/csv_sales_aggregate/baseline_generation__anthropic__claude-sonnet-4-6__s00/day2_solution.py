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

    # Check if headers are present and valid
    if reader.fieldnames is None:
        return []

    fieldnames_set = set(f.strip() for f in reader.fieldnames if f is not None)
    if not required_fields.issubset(fieldnames_set):
        return []

    for row in reader:
        # Check all required fields exist and are non-None
        try:
            region = row.get("region")
            product = row.get("product")
            quantity_str = row.get("quantity")
            cents_str = row.get("cents")
        except Exception:
            continue

        # Skip rows with missing fields
        if region is None or product is None or quantity_str is None or cents_str is None:
            continue

        # Strip whitespace
        region = region.strip()
        product = product.strip()
        quantity_str = quantity_str.strip()
        cents_str = cents_str.strip()

        # Skip rows with empty required fields
        if not region or not product or not quantity_str or not cents_str:
            continue

        # Parse integers
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
