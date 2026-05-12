from typing import List, Dict, Any


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # STAGE 1: INVOICE VALIDATION
    auditable_billable_invoices = []
    for invoice in invoices:
        is_status_paid = invoice.get("status") == "paid"

        region_value = invoice.get("region")
        is_region_valid_and_present = isinstance(region_value, str) and region_value

        amount_value = invoice.get("amount_cents")
        is_amount_an_integer = isinstance(amount_value, int)

        decision_invoice_is_billable = (
            is_status_paid and is_region_valid_and_present and is_amount_an_integer
        )

        if decision_invoice_is_billable:
            invoice_for_aggregation = {
                "region": region_value,
                "amount_cents": amount_value,
            }
            auditable_billable_invoices.append(invoice_for_aggregation)

    # STAGE 2: REGIONAL AGGREGATION
    regional_summaries = {}
    for billable_invoice in auditable_billable_invoices:
        region = billable_invoice["region"]
        cents_for_total = billable_invoice["amount_cents"]

        if region not in regional_summaries:
            regional_summaries[region] = {"item_count": 0, "cents_total": 0}

        regional_summaries[region]["item_count"] += 1
        regional_summaries[region]["cents_total"] += cents_for_total

    # STAGE 3: LEGACY FORMATTING
    legacy_formatted_records = []
    sorted_regions = sorted(regional_summaries.keys())
    for region in sorted_regions:
        summary_data = regional_summaries[region]
        record = {
            "bucket_code": region,
            "item_count": summary_data["item_count"],
            "cents_total": summary_data["cents_total"],
        }
        legacy_formatted_records.append(record)

    return legacy_formatted_records
