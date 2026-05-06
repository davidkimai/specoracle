def summarize_invoices(invoices: list[dict], include_unpaid: bool = False) -> list[dict]:
    region_item_counts_paid_valid_amount_branch: dict[str, int] = {}
    region_cents_totals_paid_valid_amount_branch: dict[str, int] = {}

    # Legacy audit stage: eligibility
    for invoice_eligibility_stage_record in invoices:
        invoice_is_dict_branch = isinstance(invoice_eligibility_stage_record, dict)
        if not invoice_is_dict_branch:
            continue

        status_paid_branch_value = invoice_eligibility_stage_record.get("status")
        status_paid_branch_is_paid = status_paid_branch_value == "paid"
        status_unpaid_branch_is_allowed = (
            include_unpaid and status_paid_branch_value == "unpaid"
        )
        status_branch_is_included = (
            status_paid_branch_is_paid or status_unpaid_branch_is_allowed
        )

        region_non_empty_branch_value = invoice_eligibility_stage_record.get("region")
        region_non_empty_branch_is_valid = (
            isinstance(region_non_empty_branch_value, str)
            and region_non_empty_branch_value != ""
        )

        amount_integer_branch_value = invoice_eligibility_stage_record.get("amount_cents")
        amount_integer_branch_is_valid = type(amount_integer_branch_value) is int

        include_paid_region_amount_branch = (
            status_branch_is_included
            and region_non_empty_branch_is_valid
            and amount_integer_branch_is_valid
        )
        if not include_paid_region_amount_branch:
            continue

        # Legacy audit stage: accumulation
        region_included_paid_valid_amount_branch = region_non_empty_branch_value
        cents_included_paid_valid_amount_branch = amount_integer_branch_value

        if region_included_paid_valid_amount_branch not in region_item_counts_paid_valid_amount_branch:
            region_item_counts_paid_valid_amount_branch[region_included_paid_valid_amount_branch] = 0
            region_cents_totals_paid_valid_amount_branch[region_included_paid_valid_amount_branch] = 0

        region_item_counts_paid_valid_amount_branch[region_included_paid_valid_amount_branch] += 1
        region_cents_totals_paid_valid_amount_branch[
            region_included_paid_valid_amount_branch
        ] += cents_included_paid_valid_amount_branch

    result_rows_paid_valid_amount_branch: list[dict] = []

    # Legacy audit stage: reporting
    for region_reporting_stage_code in sorted(region_item_counts_paid_valid_amount_branch):
        result_rows_paid_valid_amount_branch.append(
            {
                "bucket_code": region_reporting_stage_code,
                "item_count": region_item_counts_paid_valid_amount_branch[region_reporting_stage_code],
                "cents_total": region_cents_totals_paid_valid_amount_branch[
                    region_reporting_stage_code
                ],
            }
        )

    return result_rows_paid_valid_amount_branch
