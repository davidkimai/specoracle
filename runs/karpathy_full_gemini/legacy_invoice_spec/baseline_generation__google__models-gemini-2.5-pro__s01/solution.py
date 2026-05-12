import collections
from typing import Any, Dict, List


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoices by region.

    This function filters for paid invoices with a non-empty region and an
    integer amount. It then aggregates the item count and total amount in cents
    for each region.

    Args:
        invoices: A list of invoice dictionaries. Each dictionary may contain
                  'region', 'status', and 'amount_cents'.

    Returns:
        A list of summary dictionaries, sorted alphabetically by region.
        Each summary dictionary contains the keys 'bucket_code', 'item_count',
        and 'cents_total'.
    """
    # Use a defaultdict to store aggregated counts and totals for each region.
    # This avoids manual initialization checks for each new region.
    regional_summary = collections.defaultdict(
        lambda: {"item_count": 0, "cents_total": 0}
    )

    for invoice in invoices:
        # Ensure the invoice item is a dictionary to prevent attribute errors.
        if not isinstance(invoice, dict):
            continue

        # Safely retrieve invoice attributes using .get() to handle missing keys.
        status = invoice.get("status")
        region = invoice.get("region")
        amount_cents = invoice.get("amount_cents")

        # An invoice is included only if it meets all specified criteria.
        is_valid = (
            status == "paid"
            and isinstance(region, str) and region
            and isinstance(amount_cents, int)
        )

        if is_valid:
            regional_summary[region]["item_count"] += 1
            regional_summary[region]["cents_total"] += amount_cents

    # Transform the aggregated data into the required output format.
    # The dictionary items are iterated over to build the list of results.
    result = [
        {
            "bucket_code": region,
            "item_count": data["item_count"],
            "cents_total": data["cents_total"],
        }
        for region, data in regional_summary.items()
    ]

    # Sort the results list alphabetically by the region ('bucket_code').
    result.sort(key=lambda item: item["bucket_code"])

    return result
