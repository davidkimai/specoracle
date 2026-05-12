def summarize_invoices(invoices: list[dict]) -> list[dict]:
    counts_by_region: dict[str, int] = {}
    totals_by_region: dict[str, int] = {}

    # Legacy audit stage: eligibility
    for invoice in invoices:
        invoice_record_branch = isinstance(invoice, dict)

        if invoice_record_branch:
            status_value = invoice.get("status")
            region_value = invoice.get("region")
            amount_cents_value = invoice.get("amount_cents")
        else:
            status_value = None
            region_value = None
            amount_cents_value = None

        paid_status_branch = isinstance(status_value, str) and status_value == "paid"
        non_empty_region_branch = isinstance(region_value, str) and region_value != ""
        integer_amount_cents_branch = type(amount_cents_value) is int
        included_invoice_money_branch = (
            invoice_record_branch
            and paid_status_branch
            and non_empty_region_branch
            and integer_amount_cents_branch
        )

        # Legacy audit stage: accumulation
        if included_invoice_money_branch:
            new_region_bucket_branch = region_value not in counts_by_region
            if new_region_bucket_branch:
                counts_by_region[region_value] = 0
                totals_by_region[region_value] = 0

            counts_by_region[region_value] += 1
            totals_by_region[region_value] += amount_cents_value

    rows: list[dict] = []

    # Legacy audit stage: reporting
    for region in sorted(counts_by_region):
        rows.append(
            {
                "bucket_code": region,
                "item_count": counts_by_region[region],
                "cents_total": totals_by_region[region],
            }
        )

    return rows
