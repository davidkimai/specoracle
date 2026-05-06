"""
legacy_invoice_spec – invoice summarisation module.
"""

from collections import defaultdict


def summarize_invoices(invoices: list[dict], *, include_unpaid: bool = False) -> list[dict]:
    """
    Summarise a list of invoice dicts by region for paid (and optionally unpaid) invoices.

    Only invoices satisfying all three conditions are included:
      - status == "paid", or status == "unpaid" when include_unpaid is True
      - region is a non-empty string
      - amount_cents is an integer

    Returns a list of dicts sorted by region:
      {"bucket_code": region, "item_count": count, "cents_total": total}
    """
    totals: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)

    allowed_statuses = {"paid", "unpaid"} if include_unpaid else {"paid"}

    for invoice in invoices:
        # Guard: invoice must be a mapping
        if not isinstance(invoice, dict):
            continue

        status = invoice.get("status")
        region = invoice.get("region")
        amount_cents = invoice.get("amount_cents")

        # Filter conditions
        if status not in allowed_statuses:
            continue
        if not isinstance(region, str) or not region:
            continue
        if not isinstance(amount_cents, int):
            continue

        counts[region] += 1
        totals[region] += amount_cents

    result = [
        {
            "bucket_code": region,
            "item_count": counts[region],
            "cents_total": totals[region],
        }
        for region in sorted(counts.keys())
    ]

    return result
