import csv
import io
from typing import Iterator, NamedTuple, Optional, TypedDict

# Use type hints for clarity and correctness.
class SalesRecord(NamedTuple):
    """Represents a single, validated row of sales data."""
    region: str
    product: str
    quantity: int
    cents: int


class AggregatedSales(TypedDict):
    """Represents a single row of the final aggregated output."""
    region: str
    product: str
    quantity: int
    cents: int


# Define constants to avoid magic strings and improve maintainability.
_EXPECTED_HEADERS = {"region", "product", "quantity", "cents"}


def _parse_and_validate_row(row: dict[str, str]) -> Optional[SalesRecord]:
    """
    Attempts to parse a row from a csv.DictReader.

    Returns a SalesRecord if the row is valid, otherwise None.
    A row is valid if it contains all expected fields, and quantity/cents
    are non-empty strings representing integers.
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

    return SalesRecord(
        region=region,
        product=product,
        quantity=quantity,
        cents=cents,
    )


def _stream_valid_records(csv_text: str) -> Iterator[SalesRecord]:
    """
    Yields a stream of valid SalesRecord objects from the input CSV text.

    Skips rows that are malformed, have missing fields, or contain
    non-integer values for quantity or cents.
    """
    # Use io.StringIO to treat the input string as a file-like object.
    source = io.StringIO(csv_text)
    reader = csv.DictReader(source)

    if not _EXPECTED_HEADERS.issubset(reader.fieldnames or []):
        # If headers are missing or incorrect, there are no valid records.
        return

    for row in reader:
        record = _parse_and_validate_row(row)
        if record:
            yield record


def _aggregate_data(
    records: Iterator[SalesRecord]
) -> dict[tuple[str, str], dict[str, int]]:
    """
    Aggregates a stream of sales records by (region, product).
    """
    totals: dict[tuple[str, str], dict[str, int]] = {}
    for record in records:
        key = (record.region, record.product)
        if key not in totals:
            totals[key] = {"quantity": 0, "cents": 0}

        totals[key]["quantity"] += record.quantity
        totals[key]["cents"] += record.cents

    return totals


def _format_and_sort_results(
    aggregated: dict[tuple[str, str], dict[str, int]]
) -> list[AggregatedSales]:
    """
    Converts the aggregated data dict into a sorted list of dictionaries.
    """
    result = []
    # Sort by the aggregation key (region, product) for the required order.
    for region, product in sorted(aggregated.keys()):
        sums = aggregated[(region, product)]
        result.append({
            "region": region,
            "product": product,
            "quantity": sums["quantity"],
            "cents": sums["cents"],
        })
    return result


def aggregate_sales(csv_text: str) -> list[AggregatedSales]:
    """
    Aggregates sales data from a CSV-formatted string.

    The function processes the CSV data, which is expected to have headers
    'region', 'product', 'quantity', and 'cents'. It skips any malformed rows,
    rows with missing fields, or rows where 'quantity' or 'cents' are not
    valid integers.

    The valid data is then grouped by (region, product), summing the 'quantity'
    and 'cents' for each group.

    Args:
        csv_text: A string containing the sales data in CSV format.

    Returns:
        A list of dictionaries, each representing an aggregated sales record,
        sorted by region and then by product. Each dictionary has keys
        'region', 'product', 'quantity', and 'cents'.

    Raises:
        TypeError: If the input is not a string.
    """
    if not isinstance(csv_text, str):
        raise TypeError("Input must be a string.")

    if not csv_text.strip():
        return []

    valid_records = _stream_valid_records(csv_text)
    aggregated_data = _aggregate_data(valid_records)
    sorted_results = _format_and_sort_results(aggregated_data)

    return sorted_results
