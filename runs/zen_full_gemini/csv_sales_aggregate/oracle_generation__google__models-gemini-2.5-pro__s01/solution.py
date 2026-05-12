"""
Aggregates sales data from a CSV-formatted string.
"""

import csv
import io
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def _parse_and_validate_row(
    row: Dict[str, str]
) -> Optional[Tuple[str, str, int, int]]:
    """
    Parses and validates a row from the CSV data.

    A valid row must contain non-empty values for 'region', 'product',
    'quantity', and 'cents'. 'quantity' and 'cents' must be valid integers.

    Args:
        row: A dictionary representing a row from the CSV.

    Returns:
        A tuple of (region, product, quantity, cents) if the row is valid,
        otherwise None.
    """
    try:
        region = row.get("region")
        product = row.get("product")
        quantity_str = row.get("quantity")
        cents_str = row.get("cents")

        if not all((region, product, quantity_str, cents_str)):
            return None

        quantity = int(quantity_str)
        cents = int(cents_str)

        return region, product, quantity, cents
    except (ValueError, TypeError):
        # Catches errors from int() conversion or if a field is not a string.
        return None


def aggregate_sales(csv_text: str) -> list[dict]:
    """
    Parses CSV sales data, aggregates it by region and product, and returns sorted results.

    The CSV data is expected to have the headers: 'region', 'product', 'quantity', 'cents'.
    Rows are skipped if they are malformed, have missing fields, or if 'quantity'
    or 'cents' are not valid integers.

    The aggregation sums the 'quantity' and 'cents' for each unique (region, product) pair.

    The final result is a list of dictionaries, sorted alphabetically by region and then
    by product. Each dictionary has the format:
    {'region': str, 'product': str, 'quantity': int, 'cents': int}

    Args:
        csv_text: A string containing the sales data in CSV format.

    Returns:
        A sorted list of dictionaries with aggregated sales data.

    Raises:
        TypeError: If csv_text is not a string.
    """
    if not isinstance(csv_text, str):
        raise TypeError("Input must be a string.")

    csv_file = io.StringIO(csv_text)
    reader = csv.DictReader(csv_file)

    aggregates = defaultdict(lambda: {"quantity": 0, "cents": 0})

    for row in reader:
        parsed_data = _parse_and_validate_row(row)
        if parsed_data is None:
            continue

        region, product, quantity, cents = parsed_data
        key = (region, product)

        aggregates[key]["quantity"] += quantity
        aggregates[key]["cents"] += cents

    sorted_keys = sorted(aggregates.keys())

    result = []
    for region, product in sorted_keys:
        data = aggregates[(region, product)]
        result.append(
            {
                "region": region,
                "product": product,
                "quantity": data["quantity"],
                "cents": data["cents"],
            }
        )

    return result
