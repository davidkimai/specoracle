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
    aggregated = defaultdict(lambda: {"quantity": 0, "cents": 0})
    
    reader = csv.DictReader(io.StringIO(csv_text))
    
    # Check that required headers exist
    required_fields = {"region", "product", "quantity", "cents"}
    
    if reader.fieldnames is None:
        return []
    
    # Normalize fieldnames to check for required fields
    fieldnames_set = set(f.strip() for f in reader.fieldnames if f is not None)
    if not required_fields.issubset(fieldnames_set):
        return []
    
    for row in reader:
        try:
            # Check all required fields are present and not None
            region = row.get("region")
            product = row.get("product")
            quantity_str = row.get("quantity")
            cents_str = row.get("cents")
            
            if region is None or product is None or quantity_str is None or cents_str is None:
                continue
            
            region = region.strip()
            product = product.strip()
            quantity_str = quantity_str.strip()
            cents_str = cents_str.strip()
            
            if region == "" or product == "":
                continue
            
            quantity = int(quantity_str)
            cents = int(cents_str)
            
        except (ValueError, TypeError, AttributeError):
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
    
    result.sort(key=lambda r: (r["region"], r["product"]))
    
    return result
