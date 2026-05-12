def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Legacy audit stage 1
    paid_valid_region_integer_amount_by_region: dict[str, dict[str, int]] = {}

    for invoice in invoices:
        invoice_mapping_branch = isinstance(invoice, dict)
        if not invoice_mapping_branch:
            continue

        status_value = invoice.get("status")
        status_paid_branch = status_value == "paid"
        if not status_paid_branch:
            continue

        region_value = invoice.get("region")
        non_empty_region_branch = isinstance(region_value, str) and region_value != ""
        if not non_empty_region_branch:
            continue

        amount_cents_value = invoice.get("amount_cents")
        integer_amount_cents_branch = type(amount_cents_value) is int
        if not integer_amount_cents_branch:
            continue

        # Legacy audit stage 2
        if region_value not in paid_valid_region_integer_amount_by_region:
            paid_valid_region_integer_amount_by_region[region_value] = {
                "item_count": 0,
                "cents_total": 0,
            }

        paid_valid_region_integer_amount_by_region[region_value]["item_count"] += 1
        paid_valid_region_integer_amount_by_region[region_value]["cents_total"] += amount_cents_value

    # Legacy audit stage 3
    summarized_invoice_rows: list[dict] = []
    for region_value in sorted(paid_valid_region_integer_amount_by_region):
        summarized_invoice_rows.append(
            {
                "bucket_code": region_value,
                "item_count": paid_valid_region_integer_amount_by_region[region_value]["item_count"],
                "cents_total": paid_valid_region_integer_amount_by_region[region_value]["cents_total"],
            }
        )

    return summarized_invoice_rows
