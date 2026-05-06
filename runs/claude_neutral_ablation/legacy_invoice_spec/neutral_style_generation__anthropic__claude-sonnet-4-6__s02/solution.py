from collections import defaultdict


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    totals = defaultdict(lambda: {"count": 0, "total": 0})

    for invoice in invoices:
        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        if (
            status == "paid"
            and isinstance(region, str)
            and region
            and isinstance(amount_cents, int)
        ):
            totals[region]["count"] += 1
            totals[region]["total"] += amount_cents

    result = [
        {
            "bucket_code": region,
            "item_count": data["count"],
            "cents_total": data["total"],
        }
        for region, data in totals.items()
    ]

    result.sort(key=lambda x: x["bucket_code"])
    return result
