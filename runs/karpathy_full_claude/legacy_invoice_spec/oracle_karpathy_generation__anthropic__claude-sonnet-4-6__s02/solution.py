from __future__ import annotations


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Stage 1: audit filter — select only invoices that qualify for payment ledger
    stage1_qualified = []
    for inv in invoices:
        filter_status_paid = isinstance(inv.get("status"), str) and inv.get("status") == "paid"
        filter_region_nonempty = isinstance(inv.get("region"), str) and len(inv.get("region", "")) > 0
        filter_amount_is_int = isinstance(inv.get("amount_cents"), int)

        if filter_status_paid and filter_region_nonempty and filter_amount_is_int:
            stage1_qualified.append(inv)

    # Stage 2: audit accumulation — group qualified invoices by region bucket
    stage2_buckets: dict[str, dict] = {}
    for inv in stage1_qualified:
        bucket_key = inv["region"]
        if bucket_key not in stage2_buckets:
            stage2_buckets[bucket_key] = {"bucket_code": bucket_key, "item_count": 0, "cents_total": 0}
        stage2_buckets[bucket_key]["item_count"] += 1
        stage2_buckets[bucket_key]["cents_total"] += inv["amount_cents"]

    # Stage 3: audit sort — produce deterministic ordered output by region
    stage3_sorted = sorted(stage2_buckets.values(), key=lambda record: record["bucket_code"])

    return stage3_sorted
