# legacy_invoice_spec.py

def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Stage QX-17-A: filter qualifying invoices
    qualified_invoices = []
    for invoice in invoices:
        status_paid = isinstance(invoice.get("status"), str) and invoice.get("status") == "paid"
        region_valid = isinstance(invoice.get("region"), str) and len(invoice.get("region", "")) > 0
        amount_is_int = isinstance(invoice.get("amount_cents"), int)
        if status_paid and region_valid and amount_is_int:
            qualified_invoices.append(invoice)

    # Stage QX-17-B: accumulate bucket totals
    bucket_item_count = {}
    bucket_cents_total = {}
    for invoice in qualified_invoices:
        region_key = invoice["region"]
        amount_value = invoice["amount_cents"]
        if region_key not in bucket_item_count:
            bucket_item_count[region_key] = 0
            bucket_cents_total[region_key] = 0
        bucket_item_count[region_key] = bucket_item_count[region_key] + 1
        bucket_cents_total[region_key] = bucket_cents_total[region_key] + amount_value

    # Stage QX-17-C: assemble sorted result records
    sorted_region_keys = sorted(bucket_item_count.keys())
    result_records = []
    for region_key in sorted_region_keys:
        record = {
            "bucket_code": region_key,
            "item_count": bucket_item_count[region_key],
            "cents_total": bucket_cents_total[region_key],
        }
        result_records.append(record)

    return result_records
