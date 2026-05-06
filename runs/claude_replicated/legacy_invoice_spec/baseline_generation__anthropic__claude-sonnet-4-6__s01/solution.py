"""
Module for summarizing invoices by region.
"""


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    """
    Summarize paid invoices grouped by region.

    Args:
        invoices: List of invoice dictionaries.

    Returns:
        List of summary dictionaries sorted by region with keys:
        'bucket_code', 'item_count', 'cents_total'.
    """
    totals: dict[str, dict] = {}

    for invoice in invoices:
        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        if (
            status == "paid"
            and isinstance(region, str)
            and region != ""
            and isinstance(amount_cents, int)
        ):
            if region not in totals:
                totals[region] = {"item_count": 0, "cents_total": 0}
            totals[region]["item_count"] += 1
            totals[region]["cents_total"] += amount_cents

    result = [
        {
            "bucket_code": region,
            "item_count": data["item_count"],
            "cents_total": data["cents_total"],
        }
        for region, data in sorted(totals.items())
    ]

    return result
