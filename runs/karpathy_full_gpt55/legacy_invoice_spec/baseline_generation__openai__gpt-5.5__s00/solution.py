def summarize_invoices(invoices: list[dict]) -> list[dict]:
    summaries: dict[str, dict[str, int]] = {}

    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue

        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        if (
            status == "paid"
            and isinstance(region, str)
            and region != ""
            and type(amount_cents) is int
        ):
            if region not in summaries:
                summaries[region] = {"item_count": 0, "cents_total": 0}
            summaries[region]["item_count"] += 1
            summaries[region]["cents_total"] += amount_cents

    return [
        {
            "bucket_code": region,
            "item_count": summaries[region]["item_count"],
            "cents_total": summaries[region]["cents_total"],
        }
        for region in sorted(summaries)
    ]
