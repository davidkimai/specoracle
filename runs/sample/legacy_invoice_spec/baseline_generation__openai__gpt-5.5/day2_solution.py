def summarize_invoices(invoices: list[dict], include_unpaid: bool = False) -> list[dict]:
    summaries: dict[str, dict[str, int | str]] = {}

    allowed_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}

    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue

        region = invoice.get("region")
        status = invoice.get("status")
        amount_cents = invoice.get("amount_cents")

        if (
            isinstance(region, str)
            and region != ""
            and status in allowed_statuses
            and isinstance(amount_cents, int)
            and not isinstance(amount_cents, bool)
        ):
            if region not in summaries:
                summaries[region] = {
                    "bucket_code": region,
                    "item_count": 0,
                    "cents_total": 0,
                }

            summaries[region]["item_count"] += 1  # type: ignore[operator]
            summaries[region]["cents_total"] += amount_cents  # type: ignore[operator]

    return [summaries[region] for region in sorted(summaries)]
