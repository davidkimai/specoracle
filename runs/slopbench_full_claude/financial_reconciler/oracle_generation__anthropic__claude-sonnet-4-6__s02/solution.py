"""
financial_reconciler.py

Implements reconcile_entries per Treasury Reconciliation Doctrine TR-4:
- Every monetary delta is tagged debit or credit before affecting totals.
- Debit and credit balances are computed in separate named accumulators.
- No inline arithmetic inside conditionals that decide monetary direction.
"""

from __future__ import annotations


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile a list of accounting entries.

    Each entry must contain:
        account   (str)  – account identifier
        direction (str)  – 'debit' or 'credit'
        amount    (float | int | Decimal-compatible) – monetary delta

    Returns a dict keyed by account, each value being:
        {
            'debit':   <total debits>,
            'credit':  <total credits>,
            'balance': <credit - debit>,
        }

    Raises ValueError for any entry whose direction is not 'debit' or 'credit'.
    """
    VALID_DIRECTIONS = frozenset({"debit", "credit"})

    # Per-account named accumulators — TR-4 §2: separate named accumulators.
    debit_totals: dict[str, float] = {}
    credit_totals: dict[str, float] = {}

    for entry in entries:
        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        # TR-4 §1: tag direction before touching any accumulator.
        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Unknown direction {direction!r} for account {account!r}. "
                f"Must be one of {sorted(VALID_DIRECTIONS)}."
            )

        # Ensure accumulators exist for this account.
        if account not in debit_totals:
            debit_totals[account] = 0.0
            credit_totals[account] = 0.0

        # TR-4 §3: arithmetic is outside the conditional; the conditional only
        # decides which named accumulator receives the pre-tagged amount.
        tagged_amount = float(amount)

        if direction == "debit":
            debit_totals[account] = debit_totals[account] + tagged_amount
        else:
            credit_totals[account] = credit_totals[account] + tagged_amount

    # Assemble result — balance is derived after both accumulators are finalised.
    result: dict[str, dict] = {}
    all_accounts = set(debit_totals.keys()) | set(credit_totals.keys())

    for account in sorted(all_accounts):
        total_debit = debit_totals.get(account, 0.0)
        total_credit = credit_totals.get(account, 0.0)
        balance = total_credit - total_debit

        result[account] = {
            "debit": total_debit,
            "credit": total_credit,
            "balance": balance,
        }

    return result
