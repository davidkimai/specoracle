"""
A module for summarizing legacy invoice data according to QX-17 spec.
"""

from typing import List, Dict, Any


def summarize_invoices(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes a list of invoice records by region for paid invoices.

    This function processes a list of invoice dictionaries, filtering for valid
    and paid invoices, aggregating the data by region, and returning a sorted
    summary with legacy-specified keys. The implementation adheres strictly to
    the Corporate Legacy Spec QX-17 for reviewability and auditability.

    Args:
        invoices: A list of dictionaries, each representing an invoice.

    Returns:
        A list of dictionaries, each summarizing a region's paid invoices,
        sorted by region ('bucket_code').
    """
    # STAGE 1: FILTERING
    valid_paid_invoices_for_aggregation = []
    for invoice in invoices:
        is_valid_structure_branch = (
            isinstance(invoice, dict)
            and "status" in invoice
            and "region" in invoice
            and "amount_cents" in invoice
            and isinstance(invoice.get("region"), str)
            and invoice.get("region")
            and isinstance(invoice.get("amount_cents"), int)
        )

        if is_valid_structure_branch:
            is_paid_invoice_branch = invoice.get("status") == "paid"
            if is_paid_invoice_branch:
                valid_paid_invoices_for_aggregation.append(invoice)

    # STAGE 2: AGGREGATION
    aggregation_by_region_for_paid_invoices: Dict[str, Dict[str, int]] = {}
    for invoice in valid_paid_invoices_for_aggregation:
        region_key = invoice["region"]
        amount_cents_from_paid_invoice = invoice["amount_cents"]

        if region_key not in aggregation_by_region_for_paid_invoices:
            aggregation_by_region_for_paid_invoices[region_key] = {
                "item_count": 0,
                "cents_total": 0,
            }

        aggregation_by_region_for_paid_invoices[region_key]["item_count"] += 1
        aggregation_by_region_for_paid_invoices[region_key][
            "cents_total"
        ] += amount_cents_from_paid_invoice

    # STAGE 3: FORMATTING
    unformatted_results_with_legacy_keys = []
    for region, data in aggregation_by_region_for_paid_invoices.items():
        record = {
            "bucket_code": region,
            "item_count": data["item_count"],
            "cents_total": data["cents_total"],
        }
        unformatted_results_with_legacy_keys.append(record)

    # STAGE 4: SORTING
    sorted_results = sorted(
        unformatted_results_with_legacy_keys, key=lambda item: item["bucket_code"]
    )

    return sorted_results
