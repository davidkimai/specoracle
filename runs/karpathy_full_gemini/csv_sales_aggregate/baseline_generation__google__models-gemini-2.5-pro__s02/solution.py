# Standard library imports
import csv
import io
from typing import Any, Dict, List

def aggregate_sales(csv_text: str) -> List[Dict[str, Any]]:
    """
    Aggregates sales data from a CSV string.

    The function processes a CSV string with 'region', 'product', 'quantity',
    and 'cents' headers. It groups the data by (region, product) and calculates
    the sum of 'quantity' and 'cents' for each group.

    Rows are skipped if they are malformed, have missing fields, or if
    'quantity' or 'cents' cannot be parsed as integers.

    Args:
        csv_text: A string containing the CSV data.

    Returns:
        A list of dictionaries, each representing an aggregated sales record.
        The list is sorted alphabetically by 'region' and then by 'product'.
        Each dictionary contains:
        - "region": str
        - "product": str
        - "quantity": int (sum)
        - "cents": int (sum)
    """
    aggregates: Dict[tuple[str, str], Dict[str, int]] = {}
    required_headers = {'region', 'product', 'quantity', 'cents'}

    try:
        # Use io.StringIO to treat the input string as a file-like object
        csv_file = io.StringIO(csv_text)
        reader = csv.DictReader(csv_file)

        # If required headers are missing, no valid rows will be found.
        # This check ensures we don't process files with incorrect columns.
        if not required_headers.issubset(reader.fieldnames or []):
            return []

        for row in reader:
            # 1. Validate presence of required fields
            region = row.get('region')
            product = row.get('product')
            quantity_str = row.get('quantity')
            cents_str = row.get('cents')

            if not all((region, product, quantity_str, cents_str)):
                # Skip rows with missing or empty values for required fields
                continue

            # 2. Validate and convert numeric types
            try:
                quantity = int(quantity_str)
                cents = int(cents_str)
            except (ValueError, TypeError):
                # Skip rows where quantity or cents are not valid integers
                continue

            # 3. Aggregate the data
            key = (region, product)
            if key not in aggregates:
                aggregates[key] = {'quantity': 0, 'cents': 0}

            aggregates[key]['quantity'] += quantity
            aggregates[key]['cents'] += cents

    except (csv.Error, UnicodeDecodeError):
        # Return empty list for fundamentally malformed CSV text
        return []

    # 4. Format the aggregated data into the required list of dictionaries
    result = [
        {
            'region': region,
            'product': product,
            'quantity': totals['quantity'],
            'cents': totals['cents'],
        }
        for (region, product), totals in aggregates.items()
    ]

    # 5. Sort the results by region, then by product
    result.sort(key=lambda item: (item['region'], item['product']))

    return result
