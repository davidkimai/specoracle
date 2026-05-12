from typing import List, Dict, Any

def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # STAGE_1_FILTERING
    billable_invoices = []
    for invoice in invoices:
        invoice_is_paid_branch = invoice.get("status") == "paid"

        region_value = invoice.get("region")
        invoice_has_valid_region_branch = (
            isinstance(region_value, str) and region_value != ""
        )

        invoice_has_integer_amount_branch = isinstance(
            invoice.get("amount_cents"), int
        )

        invoice_is_billable_branch = (
            invoice_is_paid_branch
            and invoice_has_valid_region_branch
            and invoice_has_integer_amount_branch
        )

        if invoice_is_billable_branch:
            billable_invoices.append(invoice)

    # STAGE_2_AGGREGATION
    regional_summary_map = {}
    for invoice in billable_invoices:
        region = invoice["region"]
        amount = invoice["amount_cents"]

        if region not in regional_summary_map:
            regional_summary_map[region] = {"item_count": 0, "cents_total": 0}

        regional_summary_map[region]["item_count"] += 1
        regional_summary_map[region]["cents_total"] += amount

    # STAGE_3_FORMATTING
    summary_records = []
    for region_code, summary_data in regional_summary_map.items():
        record = {
            "bucket_code": region_code,
            "item_count": summary_data["item_count"],
            "cents_total": summary_data["cents_total"],
        }
        summary_records.append(record)

    # STAGE_4_SORTING
    summary_records.sort(key=lambda item: item["bucket_code"])

    return summary_records
