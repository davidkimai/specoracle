DEBIT = "debit"
CREDIT = "credit"


def _tag_direction(direction: str) -> str:
    if direction == DEBIT:
        return DEBIT
    if direction == CREDIT:
        return CREDIT
    raise ValueError(f"unknown direction: {direction!r}")


def _ensure_account_accumulators(
    account,
    debit_balances: dict,
    credit_balances: dict,
) -> None:
    if account not in debit_balances:
        debit_balances[account] = 0
        credit_balances[account] = 0


def reconcile_entries(entries: list[dict]) -> dict:
    debit_balances = {}
    credit_balances = {}
    direction_accumulators = {
        DEBIT: debit_balances,
        CREDIT: credit_balances,
    }

    for entry in entries:
        account = entry["account"]
        raw_direction = entry["direction"]
        amount = entry["amount"]

        tagged_direction = _tag_direction(raw_direction)
        tagged_amount = amount

        _ensure_account_accumulators(account, debit_balances, credit_balances)

        selected_accumulator = direction_accumulators[tagged_direction]
        current_total = selected_accumulator[account]
        updated_total = current_total + tagged_amount
        selected_accumulator[account] = updated_total

    reconciled = {}
    for account in debit_balances:
        debit_total = debit_balances[account]
        credit_total = credit_balances[account]
        balance = credit_total - debit_total
        reconciled[account] = {
            "debit": debit_total,
            "credit": credit_total,
            "balance": balance,
        }

    return reconciled
