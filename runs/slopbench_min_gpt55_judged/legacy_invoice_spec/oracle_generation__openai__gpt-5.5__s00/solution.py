def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Legacy audit stage: qualification
    qualified_invoice_records = []

    for invoice in invoices:
        status_value = invoice.get("status")
        region_value = invoice.get("region")
        amount_cents_value = invoice.get("amount_cents")

        paid_branch_status_is_paid = status_value == "paid"
        region_branch_region_is_non_empty_string = (
            isinstance(region_value, str) and region_value != ""
        )
        cents_branch_amount_is_integer = type(amount_cents_value) is int

        include_branch_invoice_affects_money = (
            paid_branch_status_is_paid
            and region_branch_region_is_non_empty_string
            and cents_branch_amount_is_integer
        )

        if include_branch_invoice_affects_money:
            qualified_invoice_records.append(
                {
                    "region": region_value,
                    "amount_cents": amount_cents_value,
                }
            )

    # Legacy audit stage: aggregation
    bucket_counts = {}
    bucket_cents_totals = {}

    for qualified_invoice_record in qualified_invoice_records:
        region_value = qualified_invoice_record["region"]
        amount_cents_value = qualified_invoice_record["amount_cents"]

        if region_value not in bucket_counts:
            bucket_counts[region_value] = 0
            bucket_cents_totals[region_value] = 0

        bucket_counts[region_value] += 1
        bucket_cents_totals[region_value] += amount_cents_value

    # Legacy audit stage: reporting
    summary_rows = []

    for region_value in sorted(bucket_counts):
        summary_rows.append(
            {
                "bucket_code": region_value,
                "item_count": bucket_counts[region_value],
                "cents_total": bucket_cents_totals[region_value],
            }
        )

    return summary_rows
