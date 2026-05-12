def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile financial entries by account.

    Each entry must contain:
      - account: account identifier
      - direction: either "debit" or "credit"
      - amount: numeric amount

    Returns:
        {
            account: {
                "debit": total_debits,
                "credit": total_credits,
                "balance": total_credits - total_debits,
            },
            ...
        }

    Raises:
        ValueError: if an entry has an unknown direction.
        TypeError: if entries is not a list or an entry is not a dict.
        KeyError: if a required key is missing.
    """
    if not isinstance(entries, list):
        raise TypeError("entries must be a list of dictionaries")

    reconciled: dict = {}

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise TypeError(f"entry at index {index} must be a dictionary")

        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        if direction not in ("debit", "credit"):
            raise ValueError(f"unknown direction: {direction!r}")

        if account not in reconciled:
            reconciled[account] = {
                "debit": 0,
                "credit": 0,
                "balance": 0,
            }

        reconciled[account][direction] += amount
        reconciled[account]["balance"] = (
            reconciled[account]["credit"] - reconciled[account]["debit"]
        )

    return reconciled
