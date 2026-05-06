"""
legacy_invoice_spec: summarize_invoices implementation.
"""


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    """
    Summarize paid invoices by region.

    Parameters
    ----------
    invoices : list[dict]
        List of invoice dictionaries, each potentially containing
        'region', 'status', and 'amount_cents' keys.

    Returns
    -------
    list[dict]
        A list of summary dictionaries with keys 'bucket_code',
        'item_count', and 'cents_total', sorted by 'bucket_code'.
    """
    accumulator: dict[str, dict] = {}

    for invoice in invoices:
        # Validate required fields
        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        # Filter: status must be "paid"
        if status != "paid":
            continue

        # Filter: region must be a non-empty string
        if not isinstance(region, str) or not region:
            continue

        # Filter: amount_cents must be an integer (not bool, which is subclass of int)
        if not isinstance(amount_cents, int) or isinstance(amount_cents, bool):
            continue

        # Accumulate by region
        if region not in accumulator:
            accumulator[region] = {"bucket_code": region, "item_count": 0, "cents_total": 0}

        accumulator[region]["item_count"] += 1
        accumulator[region]["cents_total"] += amount_cents

    # Sort by region (bucket_code) and return as a list
    return sorted(accumulator.values(), key=lambda row: row["bucket_code"])
