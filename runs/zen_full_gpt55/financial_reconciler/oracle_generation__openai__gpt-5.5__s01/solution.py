_VALID_DIRECTIONS = {"debit", "credit"}


def _validated_direction(direction):
    if direction not in _VALID_DIRECTIONS:
        raise ValueError(f"unknown direction: {direction!r}")
    return direction


def _new_account_totals():
    return {
        "debit": 0,
        "credit": 0,
    }


def reconcile_entries(entries: list[dict]) -> dict:
    reconciled = {}

    for entry in entries:
        account = entry["account"]
        direction_tag = _validated_direction(entry["direction"])
        monetary_delta = entry["amount"]

        if account not in reconciled:
            reconciled[account] = _new_account_totals()

        account_totals = reconciled[account]
        current_direction_total = account_totals[direction_tag]
        updated_direction_total = current_direction_total + monetary_delta
        account_totals[direction_tag] = updated_direction_total

    result = {}

    for account, account_totals in reconciled.items():
        debit_total = account_totals["debit"]
        credit_total = account_totals["credit"]
        balance = credit_total - debit_total

        result[account] = {
            "debit": debit_total,
            "credit": credit_total,
            "balance": balance,
        }

    return result
