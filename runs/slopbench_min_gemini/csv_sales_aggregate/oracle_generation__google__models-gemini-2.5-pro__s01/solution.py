import csv
import io
from collections import defaultdict
from typing import Any, Dict, Iterator, List, NamedTuple, Tuple

# A private, immutable data structure for a single validated sales record.
# Using a NamedTuple makes the code more readable and self-documenting.
class _SalesRecord(NamedTuple):
    """Represents a single, validated row of sales data."""
    region: str
    product: str
    quantity: int
    cents: int


def _stream_valid_records(csv_text: str) -> Iterator[_SalesRecord]:
    """
    Parses CSV text and yields validated sales records, skipping malformed rows.

    This generator function handles the "dirty" work of parsing and cleaning,
    allowing downstream functions to operate on clean, structured data.

    Args:
        csv_text: A string containing CSV data.

    Yields:
        _SalesRecord instances for each valid row in the input.
    """
    # Use io.StringIO to treat the input string as a file-like object,
    # which is what the `csv` module expects.
    file_like_object = io.StringIO(csv_text)
    reader = csv.reader(file_like_object)

    try:
        # Skip the header row. The prompt implies we should be robust to
        # the contents of the file and skip bad data rows, not fail on a
        # malformed header.
        next(reader)
    except StopIteration:
        # The CSV text is empty or contains only a header.
        return

    for row in reader:
        # Rule: Skip malformed rows (e.g., wrong number of fields).
        if len(row) != 4:
            continue

        region, product, quantity_str, cents_str = row

        # Rule: Skip rows with missing region or product fields.
        if not region or not product:
            continue

        # Rule: Skip rows with non-integer quantity or cents.
        try:
            quantity = int(quantity_str)
            cents = int(cents_str)
        except (ValueError, TypeError):
            continue

        yield _SalesRecord(
            region=region,
            product=product,
            quantity=quantity,
            cents=cents
        )


def _aggregate_from_records(
    records: Iterator[_SalesRecord]
) -> Dict[Tuple[str, str], Dict[str, int]]:
    """
    Aggregates a stream of sales records by the (region, product) key.

    Args:
        records: An iterator of valid _SalesRecord objects.

    Returns:
        A dictionary mapping (region, product) tuples to dictionaries
        containing the summed "quantity" and "cents".
    """
    # defaultdict simplifies aggregation by automatically creating a new entry
    # with a default value (a zeroed-out dict) for the first time a key is seen.
    totals = defaultdict(lambda: {"quantity": 0, "cents": 0})

    for record in records:
        key = (record.region, record.product)
        totals[key]["quantity"] += record.quantity
        totals[key]["cents"] += record.cents

    return dict(totals)


def _format_and_sort_results(
    aggregated_data: Dict[Tuple[str, str], Dict[str, int]]
) -> List[Dict[str, Any]]:
    """
    Converts aggregated data into a sorted list of dictionaries.

    Args:
        aggregated_data: The output from the aggregation step.

    Returns:
        A list of dictionaries, sorted by region then product, matching
        the required output format.
    """
    result_list = [
        {
            "region": region,
            "product": product,
            "quantity": totals["quantity"],
            "cents": totals["cents"],
        }
        for (region, product), totals in aggregated_data.items()
    ]

    # Sort the list first by region (alphabetically), then by product.
    # Using a tuple as the key for `sort` is a standard and efficient way
    # to implement multi-level sorting.
    result_list.sort(key=lambda item: (item["region"], item["product"]))

    return result_list


def aggregate_sales(csv_text: str) -> List[Dict[str, Any]]:
    """
    Aggregates sales data from a CSV-formatted string.

    The function processes rows from the CSV text, skipping any that are
    malformed, have missing fields, or contain non-integer values for
    quantity or cents. It then groups the valid data by region and product,
    summing the quantity and cents for each group.

    The overall process is a clear pipeline:
    1. Stream and validate records from the raw text.
    2. Aggregate the stream of valid records.
    3. Format the aggregated data into the final sorted list.

    Args:
        csv_text: A string containing the sales data in CSV format with
                  headers: region,product,quantity,cents.

    Returns:
        A list of dictionaries, where each dictionary represents an
        aggregated sales record. The list is sorted by region and then
        by product. Each dictionary has the following shape:
        {"region": str, "product": str, "quantity": int, "cents": int}

    Raises:
        TypeError: If the input `csv_text` is not a string.
    """
    if not isinstance(csv_text, str):
        raise TypeError("Input `csv_text` must be a string.")

    valid_records = _stream_valid_records(csv_text)
    aggregated_data = _aggregate_from_records(valid_records)
    output = _format_and_sort_results(aggregated_data)

    return output
