"""
Module for summarizing invoices by region.
"""


def summarize_invoices(invoices: list[dict], *, include_unpaid: bool = False) -> list[dict]:
    """
    Summarize paid (and optionally unpaid) invoices grouped by region.

    Args:
        invoices: List of invoice dictionaries.
        include_unpaid: When True, include invoices with status "unpaid" in
                        addition to "paid". Defaults to False.

    Returns:
        List of summary dictionaries sorted by region with keys:
        'bucket_code', 'item_count', 'cents_total'.
    """
    accepted_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}

    totals: dict[str, dict] = {}

    for invoice in invoices:
        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        if (
            status in accepted_statuses
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
