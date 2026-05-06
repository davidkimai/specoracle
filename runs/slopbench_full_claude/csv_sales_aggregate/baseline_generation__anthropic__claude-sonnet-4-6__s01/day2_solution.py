import csv
import io
from collections import defaultdict


def aggregate_sales(csv_text: str, *, min_quantity: int = 0) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    
    required_fields = {"region", "product", "quantity", "cents"}
    aggregated = defaultdict(lambda: {"quantity": 0, "cents": 0})
    
    for row in reader:
        # Skip rows with missing required fields
        if not required_fields.issubset(row.keys()):
            continue
        
        region = row.get("region", "").strip()
        product = row.get("product", "").strip()
        
        # Skip rows where region or product are empty/None
        if not region or not region.strip() or not product or not product.strip():
            continue
        
        # Validate quantity and cents are integers
        try:
            quantity = int(row["quantity"])
            cents = int(row["cents"])
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
