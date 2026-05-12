def summarize_invoices(invoices: list[dict]) -> list[dict]:
    totals: dict[str, list[int]] = {}

    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue

        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        if not isinstance(region, str) or region == "":
            continue
        if status != "paid":
            continue
        if type(amount_cents) is not int:
            continue

        if region not in totals:
            totals[region] = [0, 0]

        totals[region][0] += 1
        totals[region][1] += amount_cents

    return [
        {
            "bucket_code": region,
            "item_count": totals[region][0],
            "cents_total": totals[region][1],
        }
        for region in sorted(totals)
    ]
