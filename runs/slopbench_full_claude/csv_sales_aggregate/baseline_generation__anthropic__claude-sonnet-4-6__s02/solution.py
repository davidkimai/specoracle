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
    reader = csv.DictReader(io.StringIO(csv_text))
    
    # Check that the required headers exist
    required_fields = {"region", "product", "quantity", "cents"}
    
    aggregated = defaultdict(lambda: {"quantity": 0, "cents": 0})
    
    for row in reader:
        # Skip rows missing required fields
        if not required_fields.issubset(row.keys()):
            continue
        
        # Skip rows where required fields are None (missing values in CSV)
        if any(row.get(field) is None for field in required_fields):
            continue
        
        region = row["region"].strip()
        product = row["product"].strip()
        
        # Skip rows with empty region or product
        if not region or not product:
            continue
        
        # Parse quantity and cents as integers, skip if invalid
        try:
            quantity = int(row["quantity"].strip())
            cents = int(row["cents"].strip())
        except (ValueError, AttributeError):
            continue
        
        key = (region, product)
        aggregated[key]["quantity"] += quantity
        aggregated[key]["cents"] += cents
    
    # Build result list sorted by region then product
    result = []
    for (region, product) in sorted(aggregated.keys()):
        totals = aggregated[(region, product)]
        result.append({
            "region": region,
            "product": product,
            "quantity": totals["quantity"],
            "cents": totals["cents"],
        })
    
    return result
