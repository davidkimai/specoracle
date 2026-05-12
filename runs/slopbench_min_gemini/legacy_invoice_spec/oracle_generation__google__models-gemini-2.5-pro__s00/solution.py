"""
This module provides functionality to summarize corporate invoices.
"""

from typing import List, Dict, Any


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoices by region for paid items.

    Args:
        invoices: A list of invoice records, where each record is a dictionary.

    Returns:
        A list of summary records, sorted by region, with aggregated counts
        and totals for valid, paid invoices.
    """
    # STAGE 1: FILTERING
    paid_invoices_with_valid_data = []
    for invoice in invoices:
        is_paid_status_branch = invoice.get("status") == "paid"

        region_value = invoice.get("region")
        is_valid_region_branch = (
            isinstance(region_value, str) and region_value != ""
        )

        amount_value = invoice.get("amount_cents")
        is_integer_amount_branch = isinstance(amount_value, int)

        if (
            is_paid_status_branch
            and is_valid_region_branch
            and is_integer_amount_branch
        ):
            paid_invoices_with_valid_data.append(invoice)

    # STAGE 2: AGGREGATION
    aggregation_for_paid_invoices = {}
    for valid_invoice in paid_invoices_with_valid_data:
        region = valid_invoice["region"]
        cents_for_paid_item = valid_invoice["amount_cents"]

        if region not in aggregation_for_paid_invoices:
            aggregation_for_paid_invoices[region] = {
                "item_count": 0,
                "cents_total": 0,
            }

        aggregation_for_paid_invoices[region]["item_count"] += 1
        aggregation_for_paid_invoices[region][
            "cents_total"
        ] += cents_for_paid_item

    # STAGE 3: FORMATTING
    summary_records = []
    sorted_regions = sorted(aggregation_for_paid_invoices.keys())

    for region in sorted_regions:
        region_summary = aggregation_for_paid_invoices[region]
        legacy_record = {
            "bucket_code": region,
            "item_count": region_summary["item_count"],
            "cents_total": region_summary["cents_total"],
        }
        summary_records.append(legacy_record)

    return summary_records
