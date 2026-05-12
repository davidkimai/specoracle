def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Legacy audit stage: intake filtering
    paid_region_amount_accepted_counts_by_region: dict[str, int] = {}
    paid_region_amount_accepted_cents_by_region: dict[str, int] = {}

    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue

        invoice_region_candidate = invoice.get("region")
        if not isinstance(invoice_region_candidate, str):
            continue
        if invoice_region_candidate == "":
            continue

        invoice_status_candidate = invoice.get("status")
        if invoice_status_candidate != "paid":
            continue

        invoice_amount_cents_candidate = invoice.get("amount_cents")
        if type(invoice_amount_cents_candidate) is not int:
            continue

        paid_region_amount_accepted_counts_by_region[invoice_region_candidate] = (
            paid_region_amount_accepted_counts_by_region.get(invoice_region_candidate, 0) + 1
        )
        paid_region_amount_accepted_cents_by_region[invoice_region_candidate] = (
            paid_region_amount_accepted_cents_by_region.get(invoice_region_candidate, 0)
            + invoice_amount_cents_candidate
        )

    # Legacy audit stage: sorted bucket reporting
    summary_rows: list[dict] = []
    for region_bucket_code in sorted(paid_region_amount_accepted_counts_by_region):
        summary_rows.append(
            {
                "bucket_code": region_bucket_code,
                "item_count": paid_region_amount_accepted_counts_by_region[region_bucket_code],
                "cents_total": paid_region_amount_accepted_cents_by_region[region_bucket_code],
            }
        )

    return summary_rows
