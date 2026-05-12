from typing import Any


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    summaries: dict[str, dict[str, int | str]] = {}

    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue

        region: Any = invoice.get("region")
        status: Any = invoice.get("status")
        amount_cents: Any = invoice.get("amount_cents")

        if (
            isinstance(region, str)
            and region != ""
            and status == "paid"
            and type(amount_cents) is int
        ):
            if region not in summaries:
                summaries[region] = {
                    "bucket_code": region,
                    "item_count": 0,
                    "cents_total": 0,
                }

            summaries[region]["item_count"] += 1
            summaries[region]["cents_total"] += amount_cents

    return [summaries[region] for region in sorted(summaries)]
