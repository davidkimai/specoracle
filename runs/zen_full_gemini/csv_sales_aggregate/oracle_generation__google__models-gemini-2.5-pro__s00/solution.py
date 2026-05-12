#
# A Python module for aggregating sales data from a CSV-formatted string.
#
# Per the Zen of Python:
# - The logic is split into a pure parsing helper and a main orchestrator,
#   which is simpler and more readable than a single monolithic block.
# - Control flow is kept flat using guard clauses and direct iteration,
#   avoiding deep nesting.
# - Data structures like `defaultdict` are used to make data accumulation
#   explicit and clear.
# - Invalid inputs (non-string type) raise errors rather than guessing.
# - Invalid rows (malformed data, wrong types) are skipped silently as
#   per the requirements, preventing errors from passing unless they
#   corrupt the entire CSV structure.
# - Names are chosen to be self-explanatory (e.g., `aggregates`,
#   `_parse_valid_row`).
# - The solution uses only the standard library and solves the specific
#   problem without adding unused abstractions.
#

"""
Module for aggregating sales data from a CSV string.
"""

import csv
import io
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

_SalesKey = Tuple[str, str]
_SalesTotals = Dict[str, int]
_Aggregates = Dict[_SalesKey, _SalesTotals]
_AggregatedRow = Dict[str, object]


def _parse_valid_row(
    row: Dict[str, Optional[str]]
) -> Optional[Tuple[str, str, int, int]]:
    """
    Parses and validates a row from a CSV DictReader.

    A valid row must contain non-empty values for 'region', 'product',
    'quantity', and 'cents'. 'quantity' and 'cents' must be valid integers.

    Args:
        row: A dictionary representing a single row from a csv.DictReader.

    Returns:
        A tuple of (region, product, quantity, cents) if the row is valid,
        otherwise returns None.
    """
    region = row.get("region")
    product = row.get("product")
    quantity_str = row.get("quantity")
    cents_str = row.get("cents")

    if not all((region, product, quantity_str, cents_str)):
        return None

    try:
        quantity = int(quantity_str)
        cents = int(cents_str)
    except (ValueError, TypeError):
        return None

    return region, product, quantity, cents


def _build_aggregates(reader: csv.DictReader) -> _Aggregates:
    """
    Builds a dictionary of aggregated sales data from a CSV reader.

    Args:
        reader: An instance of csv.DictReader yielding sales data rows.

    Returns:
        A dictionary where keys are (region, product) tuples and values
        are dictionaries containing the summed "quantity" and "cents".
    """
    aggregates: _Aggregates = defaultdict(lambda: {"quantity": 0, "cents": 0})

    for row in reader:
        parsed_data = _parse_valid_row(row)
        if parsed_data:
            region, product, quantity, cents = parsed_data
            key = (region, product)
            aggregates[key]["quantity"] += quantity
            aggregates[key]["cents"] += cents

    return aggregates


def _format_and_sort_result(aggregates: _Aggregates) -> List[_AggregatedRow]:
    """
    Formats the aggregated data into a sorted list of dictionaries.

    Args:
        aggregates: The aggregated sales data.

    Returns:
        A list of dictionaries, sorted by region and then by product.
    """
    result = [
        {
            "region": region,
            "product": product,
            "quantity": totals["quantity"],
            "cents": totals["cents"],
        }
        for (region, product), totals in aggregates.items()
    ]

    result.sort(key=lambda item: (item["region"], item["product"]))
    return result


def aggregate_sales(csv_text: str) -> List[_AggregatedRow]:
    """
    Aggregates sales data from a CSV-formatted string.

    The CSV data is expected to have headers: region, product, quantity, cents.
    Rows that are malformed, have missing fields, or contain non-integer
    values for quantity or cents are skipped.

    The function groups data by (region, product) and sums the quantity
    and cents for each group.

    Args:
        csv_text: A string containing the sales data in CSV format.

    Returns:
        A list of dictionaries, each representing an aggregated sales record,
        sorted by region and then by product. Each dictionary contains:
        - "region": str
        - "product": str
        - "quantity": int (sum)
        - "cents": int (sum)

    Raises:
        TypeError: If the input is not a string.
    """
    if not isinstance(csv_text, str):
        raise TypeError("Input must be a string.")

    if not csv_text.strip():
        return []

    csv_file = io.StringIO(csv_text)
    reader = csv.DictReader(csv_file)

    aggregates = _build_aggregates(reader)
    return _format_and_sort_result(aggregates)
