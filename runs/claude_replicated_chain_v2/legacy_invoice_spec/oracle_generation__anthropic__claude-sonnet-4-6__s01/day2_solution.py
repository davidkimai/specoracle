from collections import defaultdict


def summarize_invoices(invoices: list[dict], *, include_unpaid: bool = False) -> list[dict]:
    # Stage 1: Filter - audit which invoices qualify for payment processing
    allowed_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}

    stage1_paid_valid = []
    for invoice in invoices:
        region_value = invoice.get("region")
        status_value = invoice.get("status")
        amount_cents_value = invoice.get("amount_cents")

        status_is_valid = status_value in allowed_statuses
        region_is_nonempty = isinstance(region_value, str) and len(region_value) > 0
        amount_is_integer = isinstance(amount_cents_value, int) and not isinstance(amount_cents_value, bool)

        if status_is_valid and region_is_nonempty and amount_is_integer:
            stage1_paid_valid.append(invoice)

    # Stage 2: Accumulate - group qualifying invoices by region bucket
    stage2_bucket_counts = defaultdict(int)
    stage2_bucket_totals = defaultdict(int)

    for invoice in stage1_paid_valid:
        bucket_region = invoice["region"]
        stage2_bucket_counts[bucket_region] += 1
        stage2_bucket_totals[bucket_region] += invoice["amount_cents"]

    # Stage 3: Emit - produce sorted output records with legacy keys
    stage3_sorted_regions = sorted(stage2_bucket_counts.keys())

    result = []
    for region_key in stage3_sorted_regions:
        record_bucket_code = region_key
        record_item_count = stage2_bucket_counts[region_key]
        record_cents_total = stage2_bucket_totals[region_key]

        result.append({
            "bucket_code": record_bucket_code,
            "item_count": record_item_count,
            "cents_total": record_cents_total,
        })

    return result
