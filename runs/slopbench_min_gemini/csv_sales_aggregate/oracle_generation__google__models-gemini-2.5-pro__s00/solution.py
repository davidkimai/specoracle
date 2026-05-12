import csv
import io
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

# Type aliases to improve readability of complex data structures.
SalesTotals = Dict[str, int]
AggregatedData = Dict[Tuple[str, str], SalesTotals]
OutputRecord = Dict[str, Union[str, int]]


def _parse_row_values(
    row: List[str],
) -> Optional[Tuple[str, str, int, int]]:
    """
    Parses and validates the values from a single CSV row.

    A valid row must have exactly four fields. The 'quantity' and 'cents'
    fields must be parsable as non-negative integers.

    Args:
        row: A list of strings representing the fields of a CSV row.

    Returns:
        A tuple of (region, product, quantity, cents) if the row is valid,
        otherwise None.
    """
    if len(row) != 4:
        return None

    region, product, quantity_str, cents_str = row

    try:
        quantity = int(quantity_str)
        cents = int(cents_str)
    except ValueError:
        return None

    if quantity < 0 or cents < 0:
        return None

    return region, product, quantity, cents


def _format_and_sort_output(aggregates: AggregatedData) -> List[OutputRecord]:
    """
    Converts the aggregated data into a sorted list of dictionaries.

    The list is sorted first by region and then by product, both alphabetically.

    Args:
        aggregates: A dictionary mapping (region, product) tuples to
                    their sales totals.

    Returns:
        A sorted list of dictionaries in the specified output format.
    """
    output_list = []
    for (region, product), totals in aggregates.items():
        output_list.append({
            "region": region,
            "product": product,
            "quantity": totals["quantity"],
            "cents": totals["cents"],
        })

    output_list.sort(key=lambda record: (record["region"], record["product"]))
    return output_list


def aggregate_sales(csv_text: str) -> List[Dict]:
    """
    Aggregates sales data from a CSV-formatted string.

    The function processes a CSV with headers 'region', 'product', 'quantity',
    and 'cents'. It groups records by (region, product) and sums the
    'quantity' and 'cents' for each group. Rows that are malformed, have
    missing fields, or contain non-integer or negative values for quantity
    or cents are skipped.

    Args:
        csv_text: A string containing the CSV data.

    Returns:
        A list of dictionaries, where each dictionary represents an aggregated
        sales record, sorted by region and then by product.

    Raises:
        ValueError: If the CSV header is missing or does not exactly match
                    ['region', 'product', 'quantity', 'cents'].
    """
    if not csv_text.strip():
        return []

    string_file = io.StringIO(csv_text)
    reader = csv.reader(string_file)

    try:
        header = next(reader)
    except StopIteration:
        return []

    expected_header = ['region', 'product', 'quantity', 'cents']
    if header != expected_header:
        raise ValueError(
            f"Invalid CSV header. Expected {expected_header}, got {header}"
        )

    aggregates: AggregatedData = defaultdict(
        lambda: {"quantity": 0, "cents": 0}
    )

    for row in reader:
        parsed_data = _parse_row_values(row)
        if parsed_data is None:
            continue

        region, product, quantity, cents = parsed_data
        key = (region, product)
        aggregates[key]["quantity"] += quantity
        aggregates[key]["cents"] += cents

    return _format_and_sort_output(aggregates)
