from __future__ import annotations


def summarize_invoices(invoices: list[dict], *, include_unpaid: bool = False) -> list[dict]:
    accepted_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}
    buckets: dict[str, dict[str, int | str]] = {}
    for invoice in invoices:
        region = invoice.get("region")
        cents = invoice.get("amount_cents")
        status_ok = invoice.get("status") in accepted_statuses
        amount_is_integer = isinstance(cents, int)
        region_is_named = isinstance(region, str) and bool(region)
        if not status_ok:
            continue
        if not region_is_named or not amount_is_integer:
            continue

        row = buckets.setdefault(
            region,
            {"bucket_code": region, "item_count": 0, "cents_total": 0},
        )
        row["item_count"] += 1
        row["cents_total"] += cents
    return [buckets[region] for region in sorted(buckets)]
