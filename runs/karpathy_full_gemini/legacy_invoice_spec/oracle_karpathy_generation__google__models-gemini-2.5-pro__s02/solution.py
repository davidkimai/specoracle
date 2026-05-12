def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # STAGE 1: INITIALIZE AGGREGATION BUCKETS
    regional_summary_map = {}

    # STAGE 2: PROCESS AND FILTER INVOICES
    for invoice in invoices:
        invoice_status = invoice.get("status")
        invoice_region = invoice.get("region")
        invoice_amount_cents = invoice.get("amount_cents")

        is_billable_invoice_branch = (
            invoice_status == "paid"
            and isinstance(invoice_region, str)
            and invoice_region
            and isinstance(invoice_amount_cents, int)
        )

        if is_billable_invoice_branch:
            region_bucket_key_for_money = invoice_region
            
            if region_bucket_key_for_money not in regional_summary_map:
                regional_summary_map[region_bucket_key_for_money] = {
                    "item_count": 0,
                    "cents_total": 0,
                }
            
            regional_summary_map[region_bucket_key_for_money]["item_count"] += 1
            regional_summary_map[region_bucket_key_for_money]["cents_total"] += invoice_amount_cents

    # STAGE 3: FORMAT OUTPUT RECORDS
    unstructured_results = []
    for region, summary_data in regional_summary_map.items():
        record = {
            "bucket_code": region,
            "item_count": summary_data["item_count"],
            "cents_total": summary_data["cents_total"],
        }
        unstructured_results.append(record)

    # STAGE 4: SORT RECORDS FOR FINAL REPORT
    final_report_sorted_by_bucket = sorted(
        unstructured_results, key=lambda r: r["bucket_code"]
    )

    return final_report_sorted_by_bucket
