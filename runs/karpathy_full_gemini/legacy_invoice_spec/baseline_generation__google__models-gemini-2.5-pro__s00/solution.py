"""
A module for summarizing invoice data.
"""

from collections import defaultdict
from typing import List, Dict, Any


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoices by region.

    This function processes a list of invoice dictionaries, filtering for those
    that are "paid", have a valid non-empty region, and an integer amount.
    It then aggregates the count of invoices and the total amount in cents
    for each region.

    The input list is not mutated.

    Args:
        invoices: A list of dictionaries, where each dictionary represents an
                  invoice. An invoice may contain "region", "status", and
                  "amount_cents" keys.

    Returns:
        A new list of summary dictionaries, sorted alphabetically by region.
        Each summary dictionary contains the following keys:
        - "bucket_code": The region name (str).
        - "item_count": The number of paid invoices for that region (int).
        - "cents_total": The sum of 'amount_cents' for all paid invoices
                         in that region (int).
    """
    regional_summary = defaultdict(lambda: {"count": 0, "total": 0})

    for invoice in invoices:
        # Use .get() to safely access keys that might be missing.
        status = invoice.get("status")
        region = invoice.get("region")
        amount_cents = invoice.get("amount_cents")

        # Validate that the invoice meets all criteria before processing.
        # - status must be exactly "paid"
        # - region must be a non-empty string
        # - amount_cents must be an integer
        is_valid_invoice = (
            status == "paid" and
            isinstance(region, str) and region and
            isinstance(amount_cents, int)
        )

        if is_valid_invoice:
            summary = regional_summary[region]
            summary["count"] += 1
            summary["total"] += amount_cents

    # Format the aggregated data into the required output structure.
    result_list = [
        {
            "bucket_code": region,
            "item_count": data["count"],
            "cents_total": data["total"],
        }
        for region, data in regional_summary.items()
    ]

    # Sort the final list by the bucket_code (region) alphabetically.
    result_list.sort(key=lambda item: item["bucket_code"])

    return result_list
