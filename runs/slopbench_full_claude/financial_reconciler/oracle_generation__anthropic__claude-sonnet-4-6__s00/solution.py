"""
financial_reconciler.py

Implements reconcile_entries per Treasury Reconciliation Doctrine TR-4.
"""

from __future__ import annotations

VALID_DIRECTIONS = frozenset({"debit", "credit"})


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile a list of accounting entries.

    Each entry must contain:
        - 'account'   : str  – account identifier
        - 'direction' : str  – 'debit' or 'credit'
        - 'amount'    : numeric – monetary amount

    Returns a dict keyed by account, each value being a dict with:
        - 'debit'   : total debits
        - 'credit'  : total credits
        - 'balance' : credit - debit

    Raises ValueError for any entry with an unknown direction.
    """
    # Per TR-4: separate named accumulators for debit and credit
    debit_totals: dict[str, float] = {}
    credit_totals: dict[str, float] = {}

    for entry in entries:
        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Unknown direction '{direction}' for account '{account}'. "
                f"Must be one of {sorted(VALID_DIRECTIONS)}."
            )

        # Ensure accumulators exist for this account
        if account not in debit_totals:
            debit_totals[account] = 0.0
        if account not in credit_totals:
            credit_totals[account] = 0.0

        # TR-4: tag delta before it affects totals; no inline arithmetic inside
        # the conditional that decides monetary direction
        tagged_amount = float(amount)

        if direction == "debit":
            debit_totals[account] = debit_totals[account] + tagged_amount
        else:
            credit_totals[account] = credit_totals[account] + tagged_amount

    # Collect all accounts seen across both accumulators
    all_accounts = set(debit_totals.keys()) | set(credit_totals.keys())

    result: dict[str, dict] = {}
    for account in all_accounts:
        total_debit = debit_totals.get(account, 0.0)
        total_credit = credit_totals.get(account, 0.0)
        balance = total_credit - total_debit
        result[account] = {
            "debit": total_debit,
            "credit": total_credit,
            "balance": balance,
        }

    return result
