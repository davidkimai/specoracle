def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Legacy audit stage 1: eligibility review
    totals_by_region: dict[str, dict[str, int]] = {}

    for invoice in invoices:
        paid_branch_status = invoice.get("status")
        paid_branch_is_paid = paid_branch_status == "paid"

        region_branch_value = invoice.get("region")
        region_branch_is_non_empty_string = (
            isinstance(region_branch_value, str) and region_branch_value != ""
        )

        amount_branch_value = invoice.get("amount_cents")
        amount_branch_is_integer = type(amount_branch_value) is int

        include_branch_invoice_affects_money = (
            paid_branch_is_paid
            and region_branch_is_non_empty_string
            and amount_branch_is_integer
        )

        if include_branch_invoice_affects_money:
            if region_branch_value not in totals_by_region:
                totals_by_region[region_branch_value] = {
                    "item_count": 0,
                    "cents_total": 0,
                }

            totals_by_region[region_branch_value]["item_count"] += 1
            totals_by_region[region_branch_value]["cents_total"] += amount_branch_value

    # Legacy audit stage 2: sorted bucket output
    summary_rows: list[dict] = []
    for region in sorted(totals_by_region):
        summary_rows.append(
            {
                "bucket_code": region,
                "item_count": totals_by_region[region]["item_count"],
                "cents_total": totals_by_region[region]["cents_total"],
            }
        )

    return summary_rows
