DEBIT = "debit"
CREDIT = "credit"


def reconcile_entries(entries: list[dict]) -> dict:
    debit_balances = {}
    credit_balances = {}
    account_order = []
    known_accounts = set()

    for entry in entries:
        direction = entry.get("direction")
        tag = _validate_direction(direction)

        account = entry["account"]
        amount = entry["amount"]
        tagged_delta = _tag_delta(tag, amount)

        if account not in known_accounts:
            known_accounts.add(account)
            account_order.append(account)
            debit_balances[account] = 0
            credit_balances[account] = 0

        _apply_tagged_delta(
            account=account,
            tagged_delta=tagged_delta,
            debit_balances=debit_balances,
            credit_balances=credit_balances,
        )

    return _build_reconciliation(account_order, debit_balances, credit_balances)


def _validate_direction(direction):
    if direction == DEBIT:
        return DEBIT
    if direction == CREDIT:
        return CREDIT
    raise ValueError(f"unknown direction: {direction!r}")


def _tag_delta(tag, amount):
    return {
        "tag": tag,
        "amount": amount,
    }


def _apply_tagged_delta(account, tagged_delta, debit_balances, credit_balances):
    accumulators_by_tag = {
        DEBIT: debit_balances,
        CREDIT: credit_balances,
    }

    tag = tagged_delta["tag"]
    amount = tagged_delta["amount"]
    selected_balances = accumulators_by_tag[tag]

    current_total = selected_balances[account]
    updated_total = current_total + amount
    selected_balances[account] = updated_total


def _build_reconciliation(account_order, debit_balances, credit_balances):
    reconciliation = {}

    for account in account_order:
        debit_total = debit_balances[account]
        credit_total = credit_balances[account]
        balance = credit_total - debit_total

        reconciliation[account] = {
            DEBIT: debit_total,
            CREDIT: credit_total,
            "balance": balance,
        }

    return reconciliation
