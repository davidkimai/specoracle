import csv
import io
from collections import defaultdict

def aggregate_sales(csv_text: str) -> list[dict]:
    """
    Aggregates sales data from a CSV text.

    The function parses a CSV string with headers 'region', 'product',
    'quantity', and 'cents'. It groups the data by (region, product),
    summing the 'quantity' and 'cents' for each group. Rows that are
    malformed, have missing fields, or contain non-integer values for
    quantity or cents are skipped.

    Args:
        csv_text: A string containing the CSV data.

    Returns:
        A list of dictionaries, with each dictionary representing an
        aggregated record. The list is sorted alphabetically by region,
        and then by product. Each dictionary has the keys 'region',
        'product', 'quantity', and 'cents'.
    """
    f = io.StringIO(csv_text)
    reader = csv.reader(f)

    try:
        # Skip the header row.
        next(reader)
    except StopIteration:
        # Handle empty or header-only CSV text.
        return []

    # Use a defaultdict to simplify the aggregation logic. The key is a
    # (region, product) tuple, and the value is a dict for totals.
    aggregated_data = defaultdict(lambda: {"quantity": 0, "cents": 0})

    for row in reader:
        # 1. Skip malformed rows (incorrect number of columns).
        if len(row) != 4:
            continue

        region, product, quantity_str, cents_str = row

        # 2. Skip rows with any missing fields.
        if not all((region, product, quantity_str, cents_str)):
            continue

        # 3. Skip rows where quantity or cents are not valid integers.
        try:
            quantity = int(quantity_str)
            cents = int(cents_str)
        except ValueError:
            continue

        # If the row is valid, add its data to the aggregate totals.
        key = (region, product)
        aggregated_data[key]["quantity"] += quantity
        aggregated_data[key]["cents"] += cents

    # Format the aggregated data into the required list of dictionaries.
    result = [
        {
            "region": region,
            "product": product,
            "quantity": totals["quantity"],
            "cents": totals["cents"],
        }
        for (region, product), totals in aggregated_data.items()
    ]

    # Sort the results by region, then by product, as required.
    result.sort(key=lambda item: (item["region"], item["product"]))

    return result
