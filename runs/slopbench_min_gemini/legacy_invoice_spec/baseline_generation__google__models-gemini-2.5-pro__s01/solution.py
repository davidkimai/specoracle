"""
A module for summarizing invoice data based on specified criteria.
"""

import collections
from typing import Any, Dict, List


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoices by region.

    This function filters a list of invoices to include only those that are
    'paid', have a non-empty 'region' string, and an integer 'amount_cents'.
    It then groups these valid invoices by region, calculating the total count
    and sum of amounts for each.

    The function does not mutate the input list.

    Args:
        invoices: A list of dictionaries, where each dictionary represents
                  an invoice and may contain 'status', 'region', and
                  'amount_cents' keys.

    Returns:
        A new list of dictionaries, sorted alphabetically by region
        ('bucket_code'). Each dictionary contains the summary for a region with
        the exact keys: 'bucket_code', 'item_count', and 'cents_total'.
    """
    regional_summary = collections.defaultdict(
        lambda: {"item_count": 0, "cents_total": 0}
    )

    for invoice in invoices:
        status = invoice.get("status")
        region = invoice.get("region")
        amount_cents = invoice.get("amount_cents")

        # An invoice is included only if it meets all specified criteria.
        if (
            status == "paid"
            and isinstance(region, str)
            and region
            and isinstance(amount_cents, int)
        ):
            regional_summary[region]["item_count"] += 1
            regional_summary[region]["cents_total"] += amount_cents

    # Transform the aggregated data into the desired list of dictionaries format.
    result = [
        {
            "bucket_code": region,
            "item_count": data["item_count"],
            "cents_total": data["cents_total"],
        }
        for region, data in regional_summary.items()
    ]

    # Sort the results by the bucket_code (region) alphabetically.
    result.sort(key=lambda item: item["bucket_code"])

    return result
