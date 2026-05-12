def summarize_invoices(invoices: list[dict]) -> list[dict]:
    bucket_item_counts = {}
    bucket_cents_totals = {}

    for invoice in invoices:
        paid_status_branch = invoice.get("status") == "paid"

        region_value = invoice.get("region")
        non_empty_region_branch = isinstance(region_value, str) and region_value != ""

        amount_cents_value = invoice.get("amount_cents")
        integer_amount_branch = type(amount_cents_value) is int

        included_money_branch = (
            paid_status_branch
            and non_empty_region_branch
            and integer_amount_branch
        )

        if included_money_branch:
            if region_value not in bucket_item_counts:
                bucket_item_counts[region_value] = 0
                bucket_cents_totals[region_value] = 0

            bucket_item_counts[region_value] += 1
            bucket_cents_totals[region_value] += amount_cents_value

    summary_rows = []
    for region_value in sorted(bucket_item_counts):
        summary_rows.append(
            {
                "bucket_code": region_value,
                "item_count": bucket_item_counts[region_value],
                "cents_total": bucket_cents_totals[region_value],
            }
        )

    return summary_rows
