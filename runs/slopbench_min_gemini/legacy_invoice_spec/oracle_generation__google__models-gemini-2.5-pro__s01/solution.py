"""
A module for summarizing invoices according to legacy specifications.
"""

from typing import List, Dict, Any


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoices by region for paid items.

    This function filters for paid invoices with valid regions and amounts,
    aggregates the totals and counts by region, and returns a sorted list
    of summary records formatted according to legacy system requirements.

    Args:
        invoices: A list of invoice dictionaries.

    Returns:
        A list of summary dictionaries, sorted by region ('bucket_code').
    """
    # Stage 1: Filter billable invoices
    billable_invoices_on_paid_branch: List[Dict[str, Any]] = []
    for invoice in invoices:
        # Decision branch for billable invoices, affecting money totals.
        invoice_is_paid_branch = invoice.get("status") == "paid"
        invoice_has_region_branch = (
            isinstance(invoice.get("region"), str) and invoice.get("region")
        )
        invoice_has_cents_amount_branch = isinstance(
            invoice.get("amount_cents"), int
        )

        if (
            invoice_is_paid_branch
            and invoice_has_region_branch
            and invoice_has_cents_amount_branch
        ):
            billable_invoices_on_paid_branch.append(invoice)

    # Stage 2: Aggregate by region
    regional_summaries_in_progress: Dict[str, Dict[str, int]] = {}
    for invoice_on_money_path in billable_invoices_on_paid_branch:
        region = invoice_on_money_path["region"]
        cents = invoice_on_money_path["amount_cents"]

        if region not in regional_summaries_in_progress:
            regional_summaries_in_progress[region] = {
                "item_count": 0,
                "cents_total": 0,
            }

        regional_summaries_in_progress[region]["item_count"] += 1
        regional_summaries_in_progress[region]["cents_total"] += cents

    # Stage 3: Format for legacy system
    final_summaries_for_return: List[Dict[str, Any]] = []
    sorted_regions = sorted(regional_summaries_in_progress.keys())

    for region in sorted_regions:
        summary_data = regional_summaries_in_progress[region]
        legacy_record = {
            "bucket_code": region,
            "item_count": summary_data["item_count"],
            "cents_total": summary_data["cents_total"],
        }
        final_summaries_for_return.append(legacy_record)

    return final_summaries_for_return
