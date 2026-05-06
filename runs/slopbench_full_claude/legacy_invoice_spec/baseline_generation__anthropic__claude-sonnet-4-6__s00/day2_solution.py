"""
legacy_invoice_spec: summarize_invoices implementation.
"""


def summarize_invoices(invoices: list[dict], *, include_unpaid: bool = False) -> list[dict]:
    """
    Summarize paid (and optionally unpaid) invoices by region.

    Parameters
    ----------
    invoices : list[dict]
        Each dict may contain 'region', 'status', and 'amount_cents' keys.
    include_unpaid : bool, optional
        When True, include invoices with status 'unpaid' in addition to 'paid'.
        Defaults to False (original behavior: paid only).

    Returns
    -------
    list[dict]
        Aggregated rows with keys 'bucket_code', 'item_count', 'cents_total',
        sorted by region (bucket_code).
    """
    allowed_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}
    accumulator: dict[str, dict] = {}

    for invoice in invoices:
        # Validate required fields
        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        # Filter conditions
        if status not in allowed_statuses:
            continue
        if not isinstance(region, str) or not region:
            continue
        if not isinstance(amount_cents, int):
            continue

        if region not in accumulator:
            accumulator[region] = {"bucket_code": region, "item_count": 0, "cents_total": 0}

        accumulator[region]["item_count"] += 1
        accumulator[region]["cents_total"] += amount_cents

    return sorted(accumulator.values(), key=lambda row: row["bucket_code"])
