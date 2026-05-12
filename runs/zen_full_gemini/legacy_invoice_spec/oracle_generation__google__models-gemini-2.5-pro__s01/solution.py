# -*- coding: utf-8 -*-
"""
A module for summarizing legacy invoices according to Corporate Legacy Spec QX-17.
"""
from typing import List, Dict, Any


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters, groups, and summarizes a list of invoice records.

    This function adheres to the strict processing rules outlined in
    Corporate Legacy Spec QX-17 for auditability and review.

    Args:
        invoices: A list of invoice dictionaries.

    Returns:
        A list of summary dictionaries, sorted by region ('bucket_code').
    """
    # STAGE 1: FILTERING
    valid_invoices_for_aggregation_money_path: List[Dict[str, Any]] = []
    for invoice in invoices:
        # Decision: Is the status "paid"? This affects monetary totals.
        is_paid_status_branch = invoice.get("status") == "paid"
        if not is_paid_status_branch:
            continue

        # Decision: Is the region valid? This affects monetary bucketing.
        region_value = invoice.get("region")
        has_valid_region_branch = isinstance(region_value, str) and region_value
        if not has_valid_region_branch:
            continue

        # Decision: Is the amount a valid integer? This affects monetary totals.
        amount_cents_value = invoice.get("amount_cents")
        has_valid_amount_branch = isinstance(amount_cents_value, int)
        if not has_valid_amount_branch:
            continue

        # This invoice passed all checks for monetary calculation.
        valid_invoices_for_aggregation_money_path.append(
            {"region": region_value, "amount_cents": amount_cents_value}
        )

    # STAGE 2: AGGREGATION
    aggregation_by_region_money_path: Dict[str, Dict[str, int]] = {}
    for valid_invoice in valid_invoices_for_aggregation_money_path:
        region = valid_invoice["region"]
        amount_cents = valid_invoice["amount_cents"]

        if region not in aggregation_by_region_money_path:
            # Initialize the record for a new region.
            aggregation_by_region_money_path[region] = {
                "item_count": 0,
                "cents_total": 0,
            }

        # Update the record for the region.
        aggregation_by_region_money_path[region]["item_count"] += 1
        aggregation_by_region_money_path[region]["cents_total"] += amount_cents

    # STAGE 3: FORMATTING
    sorted_regions = sorted(aggregation_by_region_money_path.keys())

    final_records_for_return: List[Dict[str, Any]] = []
    for region in sorted_regions:
        summary_data = aggregation_by_region_money_path[region]
        legacy_record = {
            "bucket_code": region,
            "item_count": summary_data["item_count"],
            "cents_total": summary_data["cents_total"],
        }
        final_records_for_return.append(legacy_record)

    return final_records_for_return
