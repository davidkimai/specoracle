from dataclasses import dataclass
from typing import Any

DEBIT = "debit"
CREDIT = "credit"

_ZERO = 0


@dataclass(frozen=True)
class _TaggedDelta:
    account: Any
    direction: str
    amount: Any


def reconcile_entries(entries: list[dict]) -> dict:
    debit_totals: dict[Any, Any] = {}
    credit_totals: dict[Any, Any] = {}
    accounts_in_order: list[Any] = []
    accounts_seen: set[Any] = set()

    for entry in entries:
        tagged_delta = _tag_entry(entry)

        if tagged_delta.account not in accounts_seen:
            accounts_seen.add(tagged_delta.account)
            accounts_in_order.append(tagged_delta.account)

        _apply_tagged_delta(tagged_delta, debit_totals, credit_totals)

    reconciled_accounts: dict[Any, dict[str, Any]] = {}

    for account in accounts_in_order:
        debit_total = _total_for_account(debit_totals, account)
        credit_total = _total_for_account(credit_totals, account)
        balance = credit_total - debit_total

        reconciled_accounts[account] = {
            "debit": debit_total,
            "credit": credit_total,
            "balance": balance,
        }

    return reconciled_accounts


def _tag_entry(entry: dict) -> _TaggedDelta:
    account = entry["account"]
    direction = _validated_direction(entry["direction"])
    amount = entry["amount"]

    return _TaggedDelta(
        account=account,
        direction=direction,
        amount=amount,
    )


def _validated_direction(direction: Any) -> str:
    if direction == DEBIT:
        return DEBIT

    if direction == CREDIT:
        return CREDIT

    raise ValueError(f"Unknown direction: {direction!r}")


def _apply_tagged_delta(
    tagged_delta: _TaggedDelta,
    debit_totals: dict[Any, Any],
    credit_totals: dict[Any, Any],
) -> None:
    if tagged_delta.direction == DEBIT:
        _record_debit(tagged_delta.account, tagged_delta.amount, debit_totals)
        return

    if tagged_delta.direction == CREDIT:
        _record_credit(tagged_delta.account, tagged_delta.amount, credit_totals)
        return

    raise ValueError(f"Unknown direction: {tagged_delta.direction!r}")


def _record_debit(account: Any, amount: Any, debit_totals: dict[Any, Any]) -> None:
    updated_debit_total = _updated_total(debit_totals, account, amount)
    debit_totals[account] = updated_debit_total


def _record_credit(account: Any, amount: Any, credit_totals: dict[Any, Any]) -> None:
    updated_credit_total = _updated_total(credit_totals, account, amount)
    credit_totals[account] = updated_credit_total


def _updated_total(totals: dict[Any, Any], account: Any, amount: Any) -> Any:
    if account in totals:
        current_total = totals[account]
        updated_total = current_total + amount
        return updated_total

    return amount


def _total_for_account(totals: dict[Any, Any], account: Any) -> Any:
    if account in totals:
        return totals[account]

    return _ZERO
