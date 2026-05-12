"""
A Python module for summarizing legacy invoice data.
"""

def summarize_invoices(invoices: list[dict]) -> list[dict]:
    """
    Summarizes paid invoices by region.

    This function filters a list of invoice dictionaries to include only those
    that meet specific criteria: a status of "paid", a non-empty "region"
    string, and an integer "amount_cents". It then aggregates this data by
    region, calculating the total number of invoices and the sum of their
    amounts.

    The function is designed to be safe and predictable:
    - It does not mutate the input list of invoices.
    - It gracefully handles invoices that are missing required keys or have
      values of the wrong type.

    Args:
        invoices: A list of dictionaries, where each dictionary represents
                  an invoice and may contain "region", "status", and
                  "amount_cents" keys.

    Returns:
        A new list of dictionaries, where each dictionary summarizes the
        data for a single region. The list is sorted alphabetically by region.
        Each summary dictionary contains the following keys:
        - "bucket_code": The region name (string).
        - "item_count": The number of paid invoices in that region (int).
        - "cents_total": The sum of "amount_cents" for all paid invoices
                         in that region (int).
    """
    # Use a dictionary to aggregate data by region.
    # Key: region name (str)
    # Value: a dictionary with "count" and "total" (dict[str, int])
    region_summary: dict[str, dict[str, int]] = {}

    for invoice in invoices:
        # Safely get potential values from the invoice dictionary using .get()
        # to avoid KeyErrors if a key is missing.
        status = invoice.get("status")
        region = invoice.get("region")
        amount_cents = invoice.get("amount_cents")

        # An invoice is considered valid if and only if all conditions are met:
        # 1. The status is exactly "paid".
        # 2. The region is a string and is not empty.
        # 3. The amount is an integer.
        is_valid = (
            status == "paid" and
            isinstance(region, str) and
            region and
            isinstance(amount_cents, int)
        )

        if is_valid:
            # If this is the first time we've seen this region, initialize its
            # entry in our summary dictionary.
            if region not in region_summary:
                region_summary[region] = {"count": 0, "total": 0}

            # Aggregate the data for the valid invoice.
            region_summary[region]["count"] += 1
            # We have already asserted that amount_cents is an int.
            region_summary[region]["total"] += amount_cents

    # Transform the aggregated data from the internal dictionary format to the
    # required list of dictionaries format.
    result = [
        {
            "bucket_code": region,
            "item_count": data["count"],
            "cents_total": data["total"],
        }
        for region, data in region_summary.items()
    ]

    # Sort the final list alphabetically by the "bucket_code" (region name)
    # before returning it. `sorted()` creates a new list.
    return sorted(result, key=lambda item: item["bucket_code"])
