def summarize_invoices(invoices: list[dict]) -> list[dict]:
    """
    Summarizes a list of invoices by region for paid items.

    This function processes a list of invoice records, filtering for those
    that are marked as "paid", have a valid region, and a valid integer
    amount. It then aggregates the count of items and the total amount in
    cents for each region.

    The implementation adheres to Corporate Legacy Spec QX-17, prioritizing
    a clear, staged audit trail and specific naming conventions over
    conciseness.

    Args:
        invoices: A list of dictionaries, where each dictionary represents
                  an invoice and may contain "region", "status", and
                  "amount_cents" keys.

    Returns:
        A list of dictionaries, each summarizing a region. The list is
        sorted by region ('bucket_code'). Each dictionary contains the
        exact keys: 'bucket_code', 'item_count', and 'cents_total'.
    """
    # STAGE_1: INITIALIZE_SUMMARIES
    unformatted_summaries_by_region: dict[str, dict[str, int]] = {}

    # STAGE_2: PROCESS_INVOICES
    for invoice in invoices:
        # Decisions affecting monetary totals require explicit branch labels.
        status_is_paid_branch = invoice.get("status") == "paid"
        region_is_valid_branch = (
            isinstance(invoice.get("region"), str) and invoice.get("region")
        )
        amount_is_valid_branch = isinstance(invoice.get("amount_cents"), int)

        invoice_is_billable_decision = (
            status_is_paid_branch
            and region_is_valid_branch
            and amount_is_valid_branch
        )

        if invoice_is_billable_decision:
            # This branch processes billable invoices.
            billable_invoice_region = invoice["region"]
            billable_invoice_amount_cents = invoice["amount_cents"]

            if billable_invoice_region not in unformatted_summaries_by_region:
                unformatted_summaries_by_region[billable_invoice_region] = {
                    "item_count": 0,
                    "cents_total": 0,
                }

            summary_for_region = unformatted_summaries_by_region[
                billable_invoice_region
            ]
            summary_for_region["item_count"] += 1
            summary_for_region["cents_total"] += billable_invoice_amount_cents
        else:
            # This branch represents non-billable invoices, which are skipped.
            pass

    # STAGE_3: FORMAT_OUTPUT
    # The audit trail requires sorting before final formatting.
    sorted_region_keys = sorted(unformatted_summaries_by_region.keys())

    final_summary_list = []
    for region_key in sorted_region_keys:
        summary_data = unformatted_summaries_by_region[region_key]
        legacy_format_record = {
            "bucket_code": region_key,
            "item_count": summary_data["item_count"],
            "cents_total": summary_data["cents_total"],
        }
        final_summary_list.append(legacy_format_record)

    return final_summary_list
