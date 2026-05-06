"""
financial_reconciler.py

Implements reconcile_entries per Treasury Reconciliation Doctrine TR-4.
"""

from __future__ import annotations

from typing import Iterable

KNOWN_DIRECTIONS = {"debit", "credit"}


def reconcile_entries(
    entries: list[dict],
    include_zero_accounts: Iterable[str] | None = None,
) -> dict:
    """
    Reconcile a list of monetary entries per account.

    Each entry must contain:
        account   (str)  - account identifier
        direction (str)  - 'debit' or 'credit'
        amount    (numeric) - monetary amount

    Parameters
    ----------
    entries:
        List of entry dicts to reconcile.
    include_zero_accounts:
        Optional iterable of account identifiers that must appear in the
        result even when no entries exist for them.  Such accounts are
        initialised with zero debit, credit, and balance and are then
        updated normally if matching entries are present.

    Returns a dict keyed by account, each value containing:
        debit   - sum of all debit amounts
        credit  - sum of all credit amounts
        balance - credit - debit

    Raises ValueError for any unknown direction value.
    """
    debit_accumulators: dict[str, float] = {}
    credit_accumulators: dict[str, float] = {}

    # Pre-populate accounts that must always appear in the result.
    if include_zero_accounts is not None:
        for account in include_zero_accounts:
            if account not in debit_accumulators:
                debit_accumulators[account] = 0.0
                credit_accumulators[account] = 0.0

    for entry in entries:
        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        if direction not in KNOWN_DIRECTIONS:
            raise ValueError(
                f"Unknown direction '{direction}' for account '{account}'. "
                f"Accepted values: {sorted(KNOWN_DIRECTIONS)}"
            )

        if account not in debit_accumulators:
            debit_accumulators[account] = 0.0
            credit_accumulators[account] = 0.0

        tagged_debit = amount if direction == "debit" else 0.0
        tagged_credit = amount if direction == "credit" else 0.0

        debit_accumulators[account] += tagged_debit
        credit_accumulators[account] += tagged_credit

    result: dict[str, dict] = {}
    for account in debit_accumulators:
        total_debit = debit_accumulators[account]
        total_credit = credit_accumulators[account]
        balance = total_credit - total_debit
        result[account] = {
            "debit": total_debit,
            "credit": total_credit,
            "balance": balance,
        }

    return result
