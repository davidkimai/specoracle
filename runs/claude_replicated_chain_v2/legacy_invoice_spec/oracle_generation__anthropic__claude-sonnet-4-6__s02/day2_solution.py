from __future__ import annotations


def summarize_invoices(invoices: list[dict], *, include_unpaid: bool = False) -> list[dict]:
    # Stage 1: audit-filter – isolate invoices with valid status and money fields
    allowed_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}
    stage1_paid_valid = []
    for invoice in invoices:
        filter_status = invoice.get("status") in allowed_statuses
        filter_region = isinstance(invoice.get("region"), str) and len(invoice.get("region", "")) > 0
        filter_amount = isinstance(invoice.get("amount_cents"), int)
        if filter_status and filter_region and filter_amount:
            stage1_paid_valid.append(invoice)

    # Stage 2: audit-accumulate – group by region, accumulate counts and totals
    stage2_region_buckets: dict[str, dict] = {}
    for invoice in stage1_paid_valid:
        bucket_region = invoice["region"]
        bucket_cents = invoice["amount_cents"]
        if bucket_region not in stage2_region_buckets:
            stage2_region_buckets[bucket_region] = {"item_count": 0, "cents_total": 0}
        stage2_region_buckets[bucket_region]["item_count"] += 1
        stage2_region_buckets[bucket_region]["cents_total"] += bucket_cents

    # Stage 3: audit-emit – produce sorted legacy records with required keys
    stage3_sorted_regions = sorted(stage2_region_buckets.keys())
    stage3_output = []
    for region_key in stage3_sorted_regions:
        accumulated_count = stage2_region_buckets[region_key]["item_count"]
        accumulated_total = stage2_region_buckets[region_key]["cents_total"]
        record = {
            "bucket_code": region_key,
            "item_count": accumulated_count,
            "cents_total": accumulated_total,
        }
        stage3_output.append(record)

    return stage3_output
