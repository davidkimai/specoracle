from collections import defaultdict


def _qualifies(invoice: dict) -> bool:
    region_value = invoice.get("region")
    status_value = invoice.get("status")
    amount_cents_value = invoice.get("amount_cents")

    region_passes = isinstance(region_value, str) and len(region_value) > 0
    status_passes = status_value == "paid"
    amount_passes = isinstance(amount_cents_value, int) and not isinstance(amount_cents_value, bool)

    return region_passes and status_passes and amount_passes


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Stage 1: Filter qualifying invoices
    stage1_qualified = [inv for inv in invoices if _qualifies(inv)]

    # Stage 2: Accumulate totals per region bucket
    stage2_bucket_item_count = defaultdict(int)
    stage2_bucket_cents_total = defaultdict(int)

    for invoice in stage1_qualified:
        bucket_key = invoice["region"]
        stage2_bucket_item_count[bucket_key] += 1
        stage2_bucket_cents_total[bucket_key] += invoice["amount_cents"]

    # Stage 3: Build output records with legacy keys, sorted by region
    stage3_sorted_regions = sorted(stage2_bucket_item_count.keys())

    stage3_output_records = []
    for region in stage3_sorted_regions:
        record = {
            "bucket_code": region,
            "item_count": stage2_bucket_item_count[region],
            "cents_total": stage2_bucket_cents_total[region],
        }
        stage3_output_records.append(record)

    return stage3_output_records
