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
    aggregated = defaultdict(lambda: {"quantity": 0, "cents": 0})

    try:
        reader = csv.DictReader(io.StringIO(csv_text))
    except Exception:
        return []

    # Check if the CSV has the required headers
    if reader.fieldnames is None:
        # Try to read to populate fieldnames
        try:
            # Force reading headers by peeking
            pass
        except Exception:
            return []

    for row in reader:
        # Skip rows that don't have all required fields
        if row is None:
            continue

        # Check all required fields are present and not None
        if not all(field in row and row[field] is not None for field in required_fields):
            continue

        # Extract values
        region = row.get("region", "")
        product = row.get("product", "")
        quantity_str = row.get("quantity", "")
        cents_str = row.get("cents", "")

        # Skip if any key field is None
        if region is None or product is None or quantity_str is None or cents_str is None:
            continue

        # Strip whitespace
        region = region.strip()
        product = product.strip()
        quantity_str = quantity_str.strip()
        cents_str = cents_str.strip()

        # Validate and parse integer fields
        try:
            quantity = int(quantity_str)
        except (ValueError, TypeError):
            continue

        try:
            cents = int(cents_str)
        except (ValueError, TypeError):
            continue

        key = (region, product)
        aggregated[key]["quantity"] += quantity
        aggregated[key]["cents"] += cents

    result = []
    for (region, product), totals in aggregated.items():
        result.append({
            "region": region,
            "product": product,
            "quantity": totals["quantity"],
            "cents": totals["cents"],
        })

    result.sort(key=lambda x: (x["region"], x["product"]))
    return result
