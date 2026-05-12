# -*- coding: utf-8 -*-
"""
A module for aggregating sales data from a CSV text.
"""

import csv
import io
from typing import Dict, List, Tuple

def aggregate_sales(csv_text: str) -> List[Dict[str, any]]:
    """
    Parses CSV text, aggregates sales data, and returns sorted results.

    The function processes a CSV input with headers 'region', 'product',
    'quantity', and 'cents'. It groups data by (region, product) and
    sums the 'quantity' and 'cents' for each group.

    Rows are skipped if they are malformed, have missing fields, or if
    'quantity' or 'cents' are not valid non-negative integers.

    Args:
        csv_text: A string containing the CSV data.

    Returns:
        A list of dictionaries, where each dictionary represents an aggregated
        record with keys 'region', 'product', 'quantity', and 'cents'.
        The list is sorted alphabetically by region, then by product.
    """
    aggregates: Dict[Tuple[str, str], Dict[str, int]] = {}
    
    # Use io.StringIO to treat the input string as a file-like object
    # for the csv module.
    f = io.StringIO(csv_text)
    
    # csv.DictReader conveniently maps CSV rows to dictionaries.
    reader = csv.DictReader(f)
    
    # Define the set of required headers for validation.
    expected_headers = {"region", "product", "quantity", "cents"}
    if not expected_headers.issubset(reader.fieldnames or []):
        # If the essential headers are not present, no processing can be done.
        return []

    for row in reader:
        # Extract values, defaulting to None if a key is missing.
        region = row.get("region")
        product = row.get("product")
        quantity_str = row.get("quantity")
        cents_str = row.get("cents")

        # Skip row if any of the required fields are missing or empty.
        if not all((region, product, quantity_str, cents_str)):
            continue

        try:
            # Convert quantity and cents to integers.
            quantity = int(quantity_str)
            cents = int(cents_str)
            
            # Skip row if values are negative, as they are not valid for sales.
            if quantity < 0 or cents < 0:
                continue
        except (ValueError, TypeError):
            # Skip row if conversion to integer fails.
            continue
            
        # Use a tuple of (region, product) as the key for aggregation.
        key = (region, product)
        
        # Initialize the record if this is the first time we see this key.
        if key not in aggregates:
            aggregates[key] = {"quantity": 0, "cents": 0}
        
        # Add the current row's values to the totals.
        aggregates[key]["quantity"] += quantity
        aggregates[key]["cents"] += cents

    # Format the aggregated data into the required list of dictionaries.
    result = [
        {
            "region": region,
            "product": product,
            "quantity": totals["quantity"],
            "cents": totals["cents"],
        }
        for (region, product), totals in aggregates.items()
    ]
    
    # Sort the final list first by region, then by product.
    result.sort(key=lambda item: (item["region"], item["product"]))

    return result
