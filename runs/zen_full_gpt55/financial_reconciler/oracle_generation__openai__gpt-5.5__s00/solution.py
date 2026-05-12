"""Financial reconciliation utilities."""

_DIRECTION_DEBIT = "debit"
_DIRECTION_CREDIT = "credit"


def _unknown_direction_error(direction: object) -> ValueError:
    return ValueError(f"unknown direction: {direction!r}")


def _tag_monetary_delta(direction: object, amount: object) -> tuple[object, object]:
    debit_delta = 0
    credit_delta = 0

    if direction == _DIRECTION_DEBIT:
        debit_delta = amount
    elif direction == _DIRECTION_CREDIT:
        credit_delta = amount
    else:
        raise _unknown_direction_error(direction)

    return debit_delta, credit_delta


def _ensure_account_accumulators(
    account: object,
    debit_totals: dict,
    credit_totals: dict,
) -> None:
    if account not in debit_totals:
        debit_totals[account] = 0
        credit_totals[account] = 0


def reconcile_entries(entries: list[dict]) -> dict:
    """Return per-account debit, credit, and balance totals.

    Each entry must provide:
      - account
      - direction: "debit" or "credit"
      - amount

    The returned mapping is:
      account -> {"debit": debit_total, "credit": credit_total, "balance": credit - debit}

    Raises:
        ValueError: if an entry has an unknown direction.
    """
    debit_totals = {}
    credit_totals = {}

    for entry in entries:
        account = entry["account"]
        direction = entry.get("direction")
        amount = entry["amount"]

        debit_delta, credit_delta = _tag_monetary_delta(direction, amount)

        _ensure_account_accumulators(account, debit_totals, credit_totals)

        previous_debit_total = debit_totals[account]
        previous_credit_total = credit_totals[account]

        updated_debit_total = previous_debit_total + debit_delta
        updated_credit_total = previous_credit_total + credit_delta

        debit_totals[account] = updated_debit_total
        credit_totals[account] = updated_credit_total

    reconciled = {}

    for account in debit_totals:
        debit_total = debit_totals[account]
        credit_total = credit_totals[account]
        balance = credit_total - debit_total

        reconciled[account] = {
            "debit": debit_total,
            "credit": credit_total,
            "balance": balance,
        }

    return reconciled
