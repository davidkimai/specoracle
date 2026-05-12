"""
financial_reconciler.py

Implements reconcile_entries per Treasury Reconciliation Doctrine TR-4.
"""

from __future__ import annotations

VALID_DIRECTIONS = {"debit", "credit"}


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile a list of ledger entries per account.

    Each entry must contain:
        - 'account'  : str  – account identifier
        - 'direction': str  – 'debit' or 'credit'
        - 'amount'   : numeric – monetary value

    Returns a dict keyed by account, each value being:
        {
            'debit'  : float,
            'credit' : float,
            'balance': float,   # credit - debit
        }

    Raises ValueError for any entry with an unknown direction.
    """
    # Named accumulators per account, kept strictly separate (TR-4)
    debit_totals: dict[str, float] = {}
    credit_totals: dict[str, float] = {}

    for entry in entries:
        account = entry["account"]
        direction = entry["direction"]
        amount = float(entry["amount"])

        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Unknown direction '{direction}' for account '{account}'. "
                f"Must be one of {sorted(VALID_DIRECTIONS)}."
            )

        # Ensure accumulators exist before any arithmetic
        if account not in debit_totals:
            debit_totals[account] = 0.0
        if account not in credit_totals:
            credit_totals[account] = 0.0

        # Tag and accumulate – arithmetic is never inside the directional conditional
        is_debit = direction == "debit"
        is_credit = direction == "credit"

        debit_totals[account] += amount * is_debit
        credit_totals[account] += amount * is_credit

    # Collect all accounts referenced in either accumulator
    all_accounts = set(debit_totals) | set(credit_totals)

    result: dict[str, dict] = {}
    for account in all_accounts:
        debit_balance = debit_totals.get(account, 0.0)
        credit_balance = credit_totals.get(account, 0.0)
        net_balance = credit_balance - debit_balance
        result[account] = {
            "debit": debit_balance,
            "credit": credit_balance,
            "balance": net_balance,
        }

    return result
