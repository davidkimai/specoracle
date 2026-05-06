def summarize_invoices(invoices: list[dict], *, include_unpaid: bool = False) -> list[dict]:
    allowed_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}
    totals = {}
    for invoice in invoices:
        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")
        if (
            status in allowed_statuses
            and isinstance(region, str)
            and region != ""
            and isinstance(amount_cents, int)
        ):
            if region not in totals:
                totals[region] = {"item_count": 0, "cents_total": 0}
            totals[region]["item_count"] += 1
            totals[region]["cents_total"] += amount_cents
    result = [
        {"bucket_code": region, "item_count": data["item_count"], "cents_total": data["cents_total"]}
        for region, data in sorted(totals.items())
    ]
    return result
