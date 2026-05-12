def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Legacy audit stage 1: invoice eligibility
    legacy_stage_1_eligible_invoice_rows = []

    for invoice in invoices:
        paid_branch_status_value = invoice.get("status")
        paid_branch_is_paid_status = paid_branch_status_value == "paid"

        region_branch_region_value = invoice.get("region")
        region_branch_is_non_empty_string = (
            isinstance(region_branch_region_value, str)
            and region_branch_region_value != ""
        )

        amount_branch_cents_value = invoice.get("amount_cents")
        amount_branch_is_integer_cents = (
            isinstance(amount_branch_cents_value, int)
            and not isinstance(amount_branch_cents_value, bool)
        )

        if (
            paid_branch_is_paid_status
            and region_branch_is_non_empty_string
            and amount_branch_is_integer_cents
        ):
            legacy_stage_1_eligible_invoice_rows.append(
                {
                    "region": region_branch_region_value,
                    "amount_cents": amount_branch_cents_value,
                }
            )

    # Legacy audit stage 2: regional aggregation
    legacy_stage_2_region_totals = {}

    for eligible_invoice_row in legacy_stage_1_eligible_invoice_rows:
        aggregation_branch_region = eligible_invoice_row["region"]
        aggregation_branch_amount_cents = eligible_invoice_row["amount_cents"]

        if aggregation_branch_region not in legacy_stage_2_region_totals:
            legacy_stage_2_region_totals[aggregation_branch_region] = {
                "item_count": 0,
                "cents_total": 0,
            }

        legacy_stage_2_region_totals[aggregation_branch_region]["item_count"] += 1
        legacy_stage_2_region_totals[aggregation_branch_region][
            "cents_total"
        ] += aggregation_branch_amount_cents

    # Legacy audit stage 3: sorted bucket records
    legacy_stage_3_summary_rows = []

    for bucket_branch_region in sorted(legacy_stage_2_region_totals):
        bucket_branch_region_totals = legacy_stage_2_region_totals[bucket_branch_region]
        legacy_stage_3_summary_rows.append(
            {
                "bucket_code": bucket_branch_region,
                "item_count": bucket_branch_region_totals["item_count"],
                "cents_total": bucket_branch_region_totals["cents_total"],
            }
        )

    return legacy_stage_3_summary_rows
