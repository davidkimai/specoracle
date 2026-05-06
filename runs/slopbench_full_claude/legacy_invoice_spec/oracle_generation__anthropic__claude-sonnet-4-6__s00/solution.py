from collections import defaultdict


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # AUDIT STAGE 1: filter eligible invoices
    stage1_eligible = []
    for inv in invoices:
        region_val = inv.get("region")
        status_val = inv.get("status")
        amount_val = inv.get("amount_cents")

        region_ok = isinstance(region_val, str) and len(region_val) > 0
        status_paid = status_val == "paid"
        amount_is_int = isinstance(amount_val, int) and not isinstance(amount_val, bool)

        if region_ok and status_paid and amount_is_int:
            stage1_eligible.append(inv)

    # AUDIT STAGE 2: accumulate per-region buckets
    stage2_bucket_counts = defaultdict(int)
    stage2_bucket_totals = defaultdict(int)

    for inv in stage1_eligible:
        bucket_key = inv["region"]
        stage2_bucket_counts[bucket_key] += 1
        stage2_bucket_totals[bucket_key] += inv["amount_cents"]

    # AUDIT STAGE 3: build sorted output records
    stage3_sorted_regions = sorted(stage2_bucket_counts.keys())

    stage3_output = []
    for region_label in stage3_sorted_regions:
        record_bucket_code = region_label
        record_item_count = stage2_bucket_counts[region_label]
        record_cents_total = stage2_bucket_totals[region_label]

        stage3_output.append({
            "bucket_code": record_bucket_code,
            "item_count": record_item_count,
            "cents_total": record_cents_total,
        })

    return stage3_output
