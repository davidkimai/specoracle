def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Legacy audit stage: invoice eligibility
    totals_by_region = {}

    for invoice in invoices:
        invoice_branch_is_dict = isinstance(invoice, dict)
        if not invoice_branch_is_dict:
            continue

        status_value = invoice.get("status")
        region_value = invoice.get("region")
        amount_cents_value = invoice.get("amount_cents")

        paid_branch_is_paid = status_value == "paid"
        region_branch_is_non_empty_string = isinstance(region_value, str) and region_value != ""
        money_branch_amount_is_integer = type(amount_cents_value) is int

        if paid_branch_is_paid and region_branch_is_non_empty_string and money_branch_amount_is_integer:
            if region_value not in totals_by_region:
                totals_by_region[region_value] = {"item_count": 0, "cents_total": 0}
            totals_by_region[region_value]["item_count"] += 1
            totals_by_region[region_value]["cents_total"] += amount_cents_value

    # Legacy audit stage: bucket record assembly
    rows = []
    for region_value in sorted(totals_by_region):
        rows.append(
            {
                "bucket_code": region_value,
                "item_count": totals_by_region[region_value]["item_count"],
                "cents_total": totals_by_region[region_value]["cents_total"],
            }
        )

    return rows
