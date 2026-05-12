import collections
from typing import Any, Dict, List


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoices by region.

    This function filters a list of invoice dictionaries to include only those
    that have a status of "paid", a non-empty string for the "region", and
    an integer value for "amount_cents". It then aggregates the count of
    invoices and the total sum of their amounts, grouped by region.

    The input list is not mutated.

    Args:
        invoices: A list of dictionaries, where each dictionary represents
                  an invoice.

    Returns:
        A new list of dictionaries, each summarizing a region. The list is
        sorted alphabetically by region ('bucket_code'). Each dictionary
        in the returned list has the following keys:
        - "bucket_code": The region name (str).
        - "item_count": The number of paid invoices in that region (int).
        - "cents_total": The sum of 'amount_cents' for paid invoices in
                         that region (int).
    """
    # Use a defaultdict to store summaries, with [count, total] as values.
    # This avoids checking if a region key already exists in the loop.
    region_summaries = collections.defaultdict(lambda: [0, 0])

    for invoice in invoices:
        # Safely access invoice attributes using .get()
        status = invoice.get("status")
        region = invoice.get("region")
        amount_cents = invoice.get("amount_cents")

        # An invoice is included only if it meets all criteria:
        # 1. The status must be exactly "paid".
        # 2. The region must be a non-empty string.
        # 3. The amount_cents must be an integer.
        if (
            status == "paid"
            and isinstance(region, str)
            and region
            and isinstance(amount_cents, int)
        ):
            region_summaries[region][0] += 1
            region_summaries[region][1] += amount_cents

    # Transform the aggregated data into the specified output format.
    result = [
        {
            "bucket_code": region,
            "item_count": data[0],
            "cents_total": data[1],
        }
        for region, data in region_summaries.items()
    ]

    # Sort the results alphabetically by the region ('bucket_code').
    result.sort(key=lambda item: item["bucket_code"])

    return result
