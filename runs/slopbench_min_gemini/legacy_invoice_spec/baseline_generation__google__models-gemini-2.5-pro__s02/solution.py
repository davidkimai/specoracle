"""
A module for summarizing invoice data based on specific criteria.
"""

import collections
from typing import List, Dict, Any

def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoices by region for paid items.

    This function filters a list of invoice dictionaries to include only those
    that have a status of "paid", a non-empty "region" string, and an integer
    "amount_cents". It then aggregates the data by region, calculating the
    count of invoices and the total amount in cents for each region.

    The input list is not mutated.

    Args:
        invoices: A list of dictionaries, where each dictionary represents
                  an invoice and may contain "region", "status", and
                  "amount_cents" keys.

    Returns:
        A list of dictionaries, each summarizing a region. The list is
        sorted alphabetically by region. Each dictionary contains:
        - "bucket_code": The region name (string).
        - "item_count": The number of paid invoices for that region (int).
        - "cents_total": The sum of 'amount_cents' for the region (int).
    """
    # Use a defaultdict to simplify aggregation logic.
    # The lambda initializes a new entry for a region when it's first seen.
    regional_summary = collections.defaultdict(
        lambda: {"item_count": 0, "cents_total": 0}
    )

    for invoice in invoices:
        # Safely get potential values from the invoice dictionary.
        status = invoice.get("status")
        region = invoice.get("region")
        amount_cents = invoice.get("amount_cents")

        # Validate the invoice based on the specified criteria.
        # - Status must be exactly "paid".
        # - Region must be a non-empty string.
        # - Amount must be an integer.
        if (
            status == "paid" and
            isinstance(region, str) and region and
            isinstance(amount_cents, int)
        ):
            # Aggregate the valid data.
            regional_summary[region]["item_count"] += 1
            regional_summary[region]["cents_total"] += amount_cents

    # Format the aggregated data into the required output structure.
    # First, get a sorted list of regions to ensure the final output is sorted.
    sorted_regions = sorted(regional_summary.keys())

    # Then, build the result list in the correct order.
    result = [
        {
            "bucket_code": region,
            "item_count": regional_summary[region]["item_count"],
            "cents_total": regional_summary[region]["cents_total"],
        }
        for region in sorted_regions
    ]

    return result
