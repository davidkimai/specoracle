import csv
import io

def aggregate_sales(csv_text: str) -> list[dict]:
    """
    Aggregates sales data from a CSV text.

    The function parses a CSV string with 'region', 'product', 'quantity',
    and 'cents' headers. It groups the data by (region, product) and sums
    the 'quantity' and 'cents' for each group. Malformed rows, rows with
    missing fields, or rows with non-integer values for quantity or cents
    are skipped.

    Args:
        csv_text: A string containing the CSV data.

    Returns:
        A list of dictionaries, where each dictionary represents an aggregated
        record with 'region', 'product', 'quantity', and 'cents'. The list
        is sorted by region and then by product.
    """
    csv_file = io.StringIO(csv_text)
    reader = csv.DictReader(csv_file)

    aggregates: dict[tuple[str, str], dict[str, int]] = {}

    for row in reader:
        try:
            region = row.get('region')
            product = row.get('product')
            quantity_str = row.get('quantity')
            cents_str = row.get('cents')

            # Skip row if grouping keys (region, product) are missing or empty.
            if not region or not product:
                continue

            # Convert quantity and cents to integers. This will raise an
            # exception for non-integer strings (ValueError) or None values
            # from missing fields (TypeError), causing the row to be skipped.
            quantity = int(quantity_str)
            cents = int(cents_str)

            key = (region, product)
            group = aggregates.setdefault(key, {'quantity': 0, 'cents': 0})
            
            group['quantity'] += quantity
            group['cents'] += cents

        except (ValueError, TypeError):
            # This block catches errors from int() conversion, effectively
            # skipping rows with missing or malformed quantity/cents.
            continue
    
    # Format the aggregated data into the required list of dictionaries.
    result = [
        {
            'region': region,
            'product': product,
            'quantity': totals['quantity'],
            'cents': totals['cents']
        }
        for (region, product), totals in aggregates.items()
    ]

    # Sort the final list by region, then by product.
    result.sort(key=lambda item: (item['region'], item['product']))

    return result
