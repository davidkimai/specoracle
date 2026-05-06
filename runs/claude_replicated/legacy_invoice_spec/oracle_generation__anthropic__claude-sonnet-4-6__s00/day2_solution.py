# legacy_invoice_spec.py

def summarize_invoices(invoices: list[dict], *, include_unpaid: bool = False) -> list[dict]:
    # Stage 1: Filter - identify invoices eligible for audit inclusion
    accepted_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}

    stage1_eligible = []
    for invoice in invoices:
        region_value = invoice.get("region")
        status_value = invoice.get("status")
        amount_cents_value = invoice.get("amount_cents")

        filter_branch_status_ok = (status_value in accepted_statuses)
        filter_branch_region_is_nonempty = (isinstance(region_value, str) and len(region_value) > 0)
        filter_branch_amount_is_integer = isinstance(amount_cents_value, int)

        if filter_branch_status_ok and filter_branch_region_is_nonempty and filter_branch_amount_is_integer:
            stage1_eligible.append({
                "region": region_value,
                "amount_cents": amount_cents_value,
            })

    # Stage 2: Accumulate - group by region, summing counts and totals
    stage2_accumulator = {}
    for record in stage1_eligible:
        bucket_key = record["region"]
        if bucket_key not in stage2_accumulator:
            stage2_accumulator[bucket_key] = {"item_count": 0, "cents_total": 0}
        stage2_accumulator[bucket_key]["item_count"] += 1
        stage2_accumulator[bucket_key]["cents_total"] += record["amount_cents"]

    # Stage 3: Format - produce legacy output records sorted by region
    stage3_sorted_regions = sorted(stage2_accumulator.keys())
    stage3_output = []
    for region_label in stage3_sorted_regions:
        accumulated_item_count = stage2_accumulator[region_label]["item_count"]
        accumulated_cents_total = stage2_accumulator[region_label]["cents_total"]
        stage3_output.append({
            "bucket_code": region_label,
            "item_count": accumulated_item_count,
            "cents_total": accumulated_cents_total,
        })

    return stage3_output
