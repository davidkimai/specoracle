import csv
import io
from typing import Any, Dict, List

def aggregate_sales(csv_text: str) -> List[Dict[str, Any]]:
    """
    Aggregates sales data from a CSV string, grouping by region and product.

    The function parses a CSV string with 'region', 'product', 'quantity',
    and 'cents' headers. It sums the 'quantity' and 'cents' for each unique
    (region, product) pair.

    Rows are skipped if they are malformed, have missing fields, or if
    'quantity' or 'cents' are not valid integers.

    Args:
        csv_text: A string containing the CSV data.

    Returns:
        A list of dictionaries, where each dictionary represents an aggregated
        record with keys 'region', 'product', 'quantity', and 'cents'.
        The list is sorted by 'region' and then by 'product'.
    """
    aggregates: Dict[tuple[str, str], Dict[str, int]] = {}
    required_headers = {'region', 'product', 'quantity', 'cents'}

    try:
        # Use io.StringIO to treat the input string as a file-like object.
        csv_file = io.StringIO(csv_text)
        reader = csv.DictReader(csv_file)

        # If essential headers are missing, no rows can be valid.
        if not required_headers.issubset(reader.fieldnames or []):
            return []

        for row in reader:
            region = row.get('region')
            product = row.get('product')
            quantity_str = row.get('quantity')
            cents_str = row.get('cents')

            # Skip row if any required field is missing or an empty string.
            if not all((region, product, quantity_str, cents_str)):
                continue

            # Skip row if quantity or cents are not valid integers.
            try:
                quantity = int(quantity_str)
                cents = int(cents_str)
            except (ValueError, TypeError):
                continue

            # Aggregate the valid data.
            key = (region, product)
            # Use setdefault to initialize the record if the key is new.
            record = aggregates.setdefault(key, {'quantity': 0, 'cents': 0})
            record['quantity'] += quantity
            record['cents'] += cents

    except csv.Error:
        # If the CSV is fundamentally malformed (e.g., unclosed quotes),
        # return an empty list as no valid data can be processed.
        return []

    # Format the aggregated data into the required list of dictionaries.
    result_list = [
        {
            'region': region,
            'product': product,
            'quantity': totals['quantity'],
            'cents': totals['cents'],
        }
        for (region, product), totals in aggregates.items()
    ]

    # Sort the results by region (primary key) and then by product (secondary).
    result_list.sort(key=lambda item: (item['region'], item['product']))

    return result_list
