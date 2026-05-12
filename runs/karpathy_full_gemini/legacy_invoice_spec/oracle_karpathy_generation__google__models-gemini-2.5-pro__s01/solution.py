"""
A module for summarizing legacy invoice data according to spec QX-17.
"""
from typing import List, Dict, Any


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoices by region for paid items.

    This function filters for paid invoices with valid regions and integer
    amounts, then groups them by region, calculating the count and total
    amount for each.

    Args:
        invoices: A list of invoice dictionaries. Each dictionary may contain
                  'region', 'status', and 'amount_cents' keys.

    Returns:
        A list of dictionaries, sorted by region, with each dictionary
        containing 'bucket_code', 'item_count', and 'cents_total'.
    """
    # Stage 1: Filter for paid invoices with valid money fields.
    paid_invoices_with_valid_money_and_region: List[Dict[str, Any]] = []
    for invoice in invoices:
        # Decision branch for including money.
        is_paid_status_branch = invoice.get("status") == "paid"
        has_valid_region_branch = (
            isinstance(invoice.get("region"), str) and invoice.get("region")
        )
        has_integer_money_branch = isinstance(invoice.get("amount_cents"), int)

        if is_paid_status_branch and has_valid_region_branch and has_integer_money_branch:
            paid_invoices_with_valid_money_and_region.append(invoice)

    # Stage 2: Aggregate money totals by region bucket.
    regional_totals_for_paid_money: Dict[str, Dict[str, int]] = {}
    for invoice in paid_invoices_with_valid_money_and_region:
        region = invoice["region"]
        amount_cents = invoice["amount_cents"]

        if region not in regional_totals_for_paid_money:
            regional_totals_for_paid_money[region] = {
                "item_count": 0,
                "cents_total": 0,
            }

        regional_totals_for_paid_money[region]["item_count"] += 1
        regional_totals_for_paid_money[region]["cents_total"] += amount_cents

    # Stage 3: Format aggregates into legacy records.
    unstructured_summary_for_money_buckets: List[Dict[str, Any]] = []
    for region, data in regional_totals_for_paid_money.items():
        record = {
            "bucket_code": region,
            "item_count": data["item_count"],
            "cents_total": data["cents_total"],
        }
        unstructured_summary_for_money_buckets.append(record)

    # Stage 4: Sort records by bucket code for final report.
    final_report_sorted_by_bucket = sorted(
        unstructured_summary_for_money_buckets,
        key=lambda record: record["bucket_code"]
    )

    return final_report_sorted_by_bucket
