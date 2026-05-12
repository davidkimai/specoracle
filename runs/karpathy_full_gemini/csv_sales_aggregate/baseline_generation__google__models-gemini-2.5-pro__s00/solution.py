import csv
import io
from typing import Dict, List

# A set of expected headers for validation. This makes the function robust
# against CSVs with incorrect or missing columns.
_EXPECTED_HEADERS = {'region', 'product', 'quantity', 'cents'}


def aggregate_sales(csv_text: str) -> list[dict]:
    """
    Aggregates sales data from a CSV text string.

    The function parses the CSV data, groups records by region and product,
    and calculates the total quantity and cents for each group. It is designed
    to be robust against malformed data, skipping rows that are incomplete
    or have invalid data types.

    Args:
        csv_text: A string containing CSV data. The CSV must have headers:
                  'region', 'product', 'quantity', and 'cents'.

    Returns:
        A list of dictionaries, where each dictionary represents an aggregated
        sales record. The list is sorted alphabetically by region and then by
        product. Each dictionary has the following keys:
        - "region" (str): The geographical region.
        - "product" (str): The name of the product.
        - "quantity" (int): The total quantity sold for the group.
        - "cents" (int): The total value in cents for the group.
        Returns an empty list if the CSV headers are incorrect or if no valid
        data rows are found.
    """
    # Use an in-memory text buffer to allow the csv module to read the string
    csv_file = io.StringIO(csv_text)

    # DictReader automatically uses the first row as headers.
    reader = csv.DictReader(csv_file)

    # Validate that the CSV has the necessary columns. If not, we cannot
    # proceed, so we return an empty list as no valid records can be parsed.
    if not _EXPECTED_HEADERS.issubset(reader.fieldnames or []):
        return []

    # This dictionary will store the aggregated data.
    # The key is a tuple (region, product), and the value is a dictionary
    # with the summed 'quantity' and 'cents'.
    aggregates: Dict[tuple[str, str], Dict[str, int]] = {}

    for row in reader:
        # 1. Extract data safely. Using .get() prevents KeyErrors if a row
        #    is malformed and has fewer fields than the header.
        region = row.get('region')
        product = row.get('product')
        quantity_str = row.get('quantity')
        cents_str = row.get('cents')

        # 2. Skip rows with missing fields. An empty string is treated as
        #    a missing field.
        if not all((region, product, quantity_str, cents_str)):
            continue

        # 3. Validate and convert numeric fields. Skip the row if conversion fails.
        try:
            quantity = int(quantity_str)
            cents = int(cents_str)
        except (ValueError, TypeError):
            continue

        # 4. Aggregate the valid data.
        key = (region, product)
        # setdefault is an efficient way to initialize the entry for a new key.
        record = aggregates.setdefault(key, {'quantity': 0, 'cents': 0})
        record['quantity'] += quantity
        record['cents'] += cents

    # 5. Format the aggregated data into the required list of dictionaries.
    result = [
        {
            'region': region,
            'product': product,
            'quantity': totals['quantity'],
            'cents': totals['cents'],
        }
        for (region, product), totals in aggregates.items()
    ]

    # 6. Sort the results first by region, then by product, as required.
    result.sort(key=lambda item: (item['region'], item['product']))

    return result
