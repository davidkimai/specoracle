from collections import defaultdict


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Stage 1: filter eligible invoices
    stage1_eligible = []
    for invoice in invoices:
        region_value = invoice.get("region")
        status_value = invoice.get("status")
        amount_cents_value = invoice.get("amount_cents")

        filter_region_ok = isinstance(region_value, str) and len(region_value) > 0
        filter_status_ok = status_value == "paid"
        filter_amount_ok = isinstance(amount_cents_value, int)

        if filter_region_ok and filter_status_ok and filter_amount_ok:
            stage1_eligible.append(invoice)

    # Stage 2: accumulate per-region buckets
    stage2_bucket_counts = defaultdict(int)
    stage2_bucket_totals = defaultdict(int)

    for invoice in stage1_eligible:
        bucket_region_key = invoice["region"]
        stage2_bucket_counts[bucket_region_key] += 1
        stage2_bucket_totals[bucket_region_key] += invoice["amount_cents"]

    # Stage 3: assemble sorted output records
    stage3_sorted_regions = sorted(stage2_bucket_counts.keys())

    stage3_output_records = []
    for region_label in stage3_sorted_regions:
        record_bucket_code = region_label
        record_item_count = stage2_bucket_counts[region_label]
        record_cents_total = stage2_bucket_totals[region_label]

        stage3_output_records.append({
            "bucket_code": record_bucket_code,
            "item_count": record_item_count,
            "cents_total": record_cents_total,
        })

    return stage3_output_records
