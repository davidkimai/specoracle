from collections import defaultdict


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Stage 1: filter - identify invoices eligible for money aggregation
    stage1_eligible = []
    for invoice in invoices:
        region_value = invoice.get("region")
        status_value = invoice.get("status")
        amount_value = invoice.get("amount_cents")

        filter_region_ok = isinstance(region_value, str) and len(region_value) > 0
        filter_status_ok = status_value == "paid"
        filter_amount_ok = isinstance(amount_value, int)

        if filter_region_ok and filter_status_ok and filter_amount_ok:
            stage1_eligible.append(invoice)

    # Stage 2: aggregate - accumulate counts and totals per region bucket
    stage2_bucket_counts = defaultdict(int)
    stage2_bucket_totals = defaultdict(int)

    for invoice in stage1_eligible:
        bucket_key = invoice["region"]
        stage2_bucket_counts[bucket_key] += 1
        stage2_bucket_totals[bucket_key] += invoice["amount_cents"]

    # Stage 3: format - produce legacy output records sorted by region
    stage3_sorted_regions = sorted(stage2_bucket_counts.keys())
    stage3_output = []

    for region in stage3_sorted_regions:
        record_bucket_code = region
        record_item_count = stage2_bucket_counts[region]
        record_cents_total = stage2_bucket_totals[region]

        stage3_output.append({
            "bucket_code": record_bucket_code,
            "item_count": record_item_count,
            "cents_total": record_cents_total,
        })

    return stage3_output
