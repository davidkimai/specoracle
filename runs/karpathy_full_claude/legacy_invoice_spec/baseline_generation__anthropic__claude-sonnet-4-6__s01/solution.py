"""
legacy_invoice_spec: summarize_invoices implementation.
"""

from collections import defaultdict


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    """
    Summarize paid invoices by region.

    Parameters
    ----------
    invoices : list[dict]
        List of invoice dictionaries.

    Returns
    -------
    list[dict]
        Aggregated rows sorted by region with keys:
        'bucket_code', 'item_count', 'cents_total'.
    """
    totals: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)

    for invoice in invoices:
        # Validate required fields without mutating input
        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        # Filter: status must be "paid", region must be a non-empty string,
        # amount_cents must be an integer (bool is excluded as a subclass check)
        if status != "paid":
            continue
        if not isinstance(region, str) or not region:
            continue
        if not isinstance(amount_cents, int) or isinstance(amount_cents, bool):
            continue

        totals[region] += amount_cents
        counts[region] += 1

    result = [
        {
            "bucket_code": region,
            "item_count": counts[region],
            "cents_total": totals[region],
        }
        for region in sorted(totals.keys())
    ]

    return result
