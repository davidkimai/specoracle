# legacy_invoice_spec.py
# Corporate Legacy Spec QX-17 compliant implementation

from collections import defaultdict


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # AUDIT STAGE 1: filter eligible invoices
    stage1_eligible = []
    for invoice in invoices:
        region_val = invoice.get("region")
        status_val = invoice.get("status")
        amount_val = invoice.get("amount_cents")

        region_check_pass = isinstance(region_val, str) and len(region_val) > 0
        status_check_pass = status_val == "paid"
        amount_check_pass = isinstance(amount_val, int) and not isinstance(amount_val, bool)

        if region_check_pass and status_check_pass and amount_check_pass:
            stage1_eligible.append(invoice)

    # AUDIT STAGE 2: accumulate bucket totals
    stage2_bucket_counts = defaultdict(int)
    stage2_bucket_totals = defaultdict(int)

    for invoice in stage1_eligible:
        bucket_key = invoice["region"]
        stage2_bucket_counts[bucket_key] += 1
        stage2_bucket_totals[bucket_key] += invoice["amount_cents"]

    # AUDIT STAGE 3: build output records with legacy keys
    stage3_records = []
    for bucket_key in sorted(stage2_bucket_counts.keys()):
        record_bucket_code = bucket_key
        record_item_count = stage2_bucket_counts[bucket_key]
        record_cents_total = stage2_bucket_totals[bucket_key]

        stage3_records.append({
            "bucket_code": record_bucket_code,
            "item_count": record_item_count,
            "cents_total": record_cents_total,
        })

    return stage3_records
