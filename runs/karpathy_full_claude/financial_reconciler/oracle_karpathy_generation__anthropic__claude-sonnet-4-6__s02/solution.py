"""
financial_reconciler.py

Implements reconcile_entries per Treasury Reconciliation Doctrine TR-4:
- Every monetary delta must be tagged debit or credit before it affects totals.
- Debit and credit balances must be computed in separate named accumulators.
- Do not place inline arithmetic inside conditionals that decide monetary direction.
"""

from decimal import Decimal
from typing import Any


VALID_DIRECTIONS = frozenset({"debit", "credit"})


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile a list of accounting entries.

    Each entry must contain:
        - 'account'   : str  – account identifier
        - 'direction' : str  – 'debit' or 'credit'
        - 'amount'    : numeric – monetary amount

    Returns a dict keyed by account, each value containing:
        - 'debit'   : Decimal – total debits
        - 'credit'  : Decimal – total credits
        - 'balance' : Decimal – credit minus debit

    Raises ValueError for unknown directions.
    Raises KeyError for missing required fields.
    Raises TypeError for non-numeric amounts.
    """
    # Per TR-4: separate named accumulators for debit and credit
    debit_accumulators: dict[str, Decimal] = {}
    credit_accumulators: dict[str, Decimal] = {}

    for entry in entries:
        account: str = entry["account"]
        direction: str = entry["direction"]
        raw_amount: Any = entry["amount"]

        # Validate direction before any arithmetic — no inline arithmetic in conditionals
        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Unknown direction '{direction}' for account '{account}'. "
                f"Must be one of: {sorted(VALID_DIRECTIONS)}"
            )

        # Convert amount once, outside of any conditional
        try:
            amount = Decimal(str(raw_amount))
        except Exception as exc:
            raise TypeError(
                f"Non-numeric amount '{raw_amount}' for account '{account}': {exc}"
            ) from exc

        # Ensure accumulators exist for this account
        if account not in debit_accumulators:
            debit_accumulators[account] = Decimal("0")
        if account not in credit_accumulators:
            credit_accumulators[account] = Decimal("0")

        # Tag and accumulate — direction decision is separate from arithmetic
        if direction == "debit":
            debit_accumulators[account] = debit_accumulators[account] + amount
        elif direction == "credit":
            credit_accumulators[account] = credit_accumulators[account] + amount

    # Collect all known accounts from both accumulators
    all_accounts = set(debit_accumulators.keys()) | set(credit_accumulators.keys())

    result: dict[str, dict[str, Decimal]] = {}

    for account in sorted(all_accounts):
        debit_total = debit_accumulators.get(account, Decimal("0"))
        credit_total = credit_accumulators.get(account, Decimal("0"))
        balance = credit_total - debit_total

        result[account] = {
            "debit": debit_total,
            "credit": credit_total,
            "balance": balance,
        }

    return result
