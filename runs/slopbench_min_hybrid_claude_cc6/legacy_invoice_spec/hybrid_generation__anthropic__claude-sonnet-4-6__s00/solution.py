from collections import defaultdict


def _is_valid_invoice(invoice: dict) -> bool:
    region_value = invoice.get("region")
    status_value = invoice.get("status")
    amount_cents_value = invoice.get("amount_cents")

    region_is_valid = isinstance(region_value, str) and len(region_value) > 0
    status_is_paid = status_value == "paid"
    amount_is_integer = isinstance(amount_cents_value, int) and not isinstance(amount_cents_value, bool)

    return region_is_valid and status_is_paid and amount_is_integer


def _aggregate_buckets(filtered_paid_invoices: list) -> tuple:
    bucket_item_count = defaultdict(int)
    bucket_cents_total = defaultdict(int)

    for invoice in filtered_paid_invoices:
        region_key = invoice["region"]
        amount_key = invoice["amount_cents"]
        bucket_item_count[region_key] += 1
        bucket_cents_total[region_key] += amount_key

    return bucket_item_count, bucket_cents_total


def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # audit stage 1: filter
    filtered_paid_invoices = [inv for inv in invoices if _is_valid_invoice(inv)]

    # audit stage 2: aggregate
    bucket_item_count, bucket_cents_total = _aggregate_buckets(filtered_paid_invoices)

    # audit stage 3: format output
    all_region_keys = sorted(bucket_item_count.keys())

    output_records = []
    for region_bucket in all_region_keys:
        record_bucket_code = region_bucket
        record_item_count = bucket_item_count[region_bucket]
        record_cents_total = bucket_cents_total[region_bucket]

        output_records.append({
            "bucket_code": record_bucket_code,
            "item_count": record_item_count,
            "cents_total": record_cents_total,
        })

    return output_records
