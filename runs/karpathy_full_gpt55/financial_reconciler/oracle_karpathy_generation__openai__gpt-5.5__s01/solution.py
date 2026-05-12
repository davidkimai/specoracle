_DEBIT = "debit"
_CREDIT = "credit"


def _new_account_totals():
    return {
        _DEBIT: 0,
        _CREDIT: 0,
    }


def _normalize_direction(direction):
    if direction == _DEBIT:
        return _DEBIT
    if direction == _CREDIT:
        return _CREDIT
    raise ValueError(f"unknown direction: {direction!r}")


def _apply_debit(account_totals, amount):
    debit_delta = amount
    debit_accumulator = account_totals[_DEBIT]
    debit_accumulator = debit_accumulator + debit_delta
    account_totals[_DEBIT] = debit_accumulator


def _apply_credit(account_totals, amount):
    credit_delta = amount
    credit_accumulator = account_totals[_CREDIT]
    credit_accumulator = credit_accumulator + credit_delta
    account_totals[_CREDIT] = credit_accumulator


_DIRECTION_APPLIERS = {
    _DEBIT: _apply_debit,
    _CREDIT: _apply_credit,
}


def reconcile_entries(entries: list[dict]) -> dict:
    account_totals_by_account = {}

    for entry in entries:
        account = entry["account"]
        tagged_direction = _normalize_direction(entry["direction"])
        amount = entry["amount"]

        account_totals = account_totals_by_account.get(account)
        if account_totals is None:
            account_totals = _new_account_totals()
            account_totals_by_account[account] = account_totals

        apply_tagged_delta = _DIRECTION_APPLIERS[tagged_direction]
        apply_tagged_delta(account_totals, amount)

    reconciled_by_account = {}
    for account, account_totals in account_totals_by_account.items():
        debit_accumulator = account_totals[_DEBIT]
        credit_accumulator = account_totals[_CREDIT]
        balance = credit_accumulator - debit_accumulator

        reconciled_by_account[account] = {
            _DEBIT: debit_accumulator,
            _CREDIT: credit_accumulator,
            "balance": balance,
        }

    return reconciled_by_account
