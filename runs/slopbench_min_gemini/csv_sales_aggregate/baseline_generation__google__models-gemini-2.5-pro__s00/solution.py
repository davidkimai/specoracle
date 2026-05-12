# Standard library imports
import csv
import io
from collections import defaultdict

def aggregate_sales(csv_text: str) -> list[dict]:
    """
    Aggregates sales data from a CSV string.

    This function parses a CSV string with 'region', 'product', 'quantity',
    and 'cents' headers. It groups data by (region, product) pairs, summing
    the 'quantity' and 'cents' for each group.

    Rows are skipped if they are malformed, have missing fields, or if
    'quantity' or 'cents' cannot be converted to an integer.

    Args:
        csv_text: A string containing the CSV data.

    Returns:
        A list of dictionaries, with each dictionary representing the
        aggregated sales data for a unique (region, product) pair. The
        list is sorted alphabetically by region, and then by product.
        Each dictionary has the shape:
        {"region": str, "product": str, "quantity": int, "cents": int}
    """
    # Use io.StringIO to treat the input string as a file-like object,
    # which is required by the csv module.
    csv_file = io.StringIO(csv_text)

    # Use csv.DictReader for robust parsing that is not dependent on column order.
    reader = csv.DictReader(csv_file)

    # Validate that the required headers are present in the CSV.
    expected_headers = {"region", "product", "quantity", "cents"}
    if not reader.fieldnames or not expected_headers.issubset(reader.fieldnames):
        return []

    # Use a defaultdict to simplify the aggregation logic.
    # The key is a tuple (region, product).
    # The value is a dictionary holding the summed quantity and cents.
    aggregates: defaultdict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"quantity": 0, "cents": 0}
    )

    for row in reader:
        # Malformed rows with more columns than headers will have a None key.
        if None in row:
            continue

        # Extract values for required fields.
        region = row.get("region")
        product = row.get("product")
        quantity_str = row.get("quantity")
        cents_str = row.get("cents")

        # Skip rows with missing or empty string values for required fields.
        if not all((region, product, quantity_str, cents_str)):
            continue

        # Try to convert quantity and cents to integers. Skip row on failure.
        try:
            quantity = int(quantity_str)
            cents = int(cents_str)
        except (ValueError, TypeError):
            continue

        # Perform the aggregation.
        key = (region, product)
        aggregates[key]["quantity"] += quantity
        aggregates[key]["cents"] += cents

    # Format the aggregated data into the specified list of dictionaries.
    result = [
        {
            "region": region,
            "product": product,
            "quantity": data["quantity"],
            "cents": data["cents"],
        }
        for (region, product), data in aggregates.items()
    ]

    # Sort the final list first by region, then by product.
    result.sort(key=lambda item: (item["region"], item["product"]))

    return result
