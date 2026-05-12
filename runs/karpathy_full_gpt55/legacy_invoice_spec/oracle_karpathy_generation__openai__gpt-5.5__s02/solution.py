def summarize_invoices(invoices: list[dict]) -> list[dict]:
    # Legacy audit stage 1: invoice eligibility
    buckets_by_region: dict[str, dict[str, int]] = {}

    for invoice in invoices:
        invoice_branch_is_mapping = isinstance(invoice, dict)
        if not invoice_branch_is_mapping:
            continue

        status = invoice.get("status")
        region = invoice.get("region")
        amount_cents = invoice.get("amount_cents")

        paid_branch_status_is_paid = status == "paid"
        paid_branch_region_is_non_empty_string = isinstance(region, str) and region != ""
        paid_branch_amount_is_integer = type(amount_cents) is int

        if not paid_branch_status_is_paid:
            continue
        if not paid_branch_region_is_non_empty_string:
            continue
        if not paid_branch_amount_is_integer:
            continue

        # Legacy audit stage 2: bucket accumulation
        if region not in buckets_by_region:
            buckets_by_region[region] = {
                "item_count": 0,
                "cents_total": 0,
            }

        paid_branch_bucket = buckets_by_region[region]
        paid_branch_bucket["item_count"] = paid_branch_bucket["item_count"] + 1
        paid_branch_bucket["cents_total"] = paid_branch_bucket["cents_total"] + amount_cents

    # Legacy audit stage 3: sorted legacy records
    rows: list[dict] = []
    for region in sorted(buckets_by_region):
        bucket = buckets_by_region[region]
        rows.append(
            {
                "bucket_code": region,
                "item_count": bucket["item_count"],
                "cents_total": bucket["cents_total"],
            }
        )

    return rows
