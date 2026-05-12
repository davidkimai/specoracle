"""
financial_reconciler.py

Implements reconcile_entries per Treasury Reconciliation Doctrine TR-4:
  - Every monetary delta is tagged debit or credit before affecting totals.
  - Debit and credit balances are computed in separate named accumulators.
  - No inline arithmetic inside conditionals that decide monetary direction.
"""

from decimal import Decimal


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile a list of accounting entries.

    Each entry must contain:
        account   : str  - account identifier
        direction : str  - 'debit' or 'credit'
        amount    : numeric - monetary amount

    Returns a dict keyed by account, each value being:
        {
            'debit'  : Decimal,
            'credit' : Decimal,
            'balance': Decimal  (credit - debit)
        }

    Raises ValueError for any entry with an unknown direction.
    """
    VALID_DIRECTIONS = frozenset({"debit", "credit"})

    # Per TR-4: separate named accumulators for debit and credit
    debit_totals: dict[str, Decimal] = {}
    credit_totals: dict[str, Decimal] = {}

    for entry in entries:
        account = entry["account"]
        direction = entry["direction"]
        amount = Decimal(str(entry["amount"]))

        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Unknown direction '{direction}' for account '{account}'. "
                f"Must be one of {sorted(VALID_DIRECTIONS)}."
            )

        # Ensure accumulators exist for this account
        if account not in debit_totals:
            debit_totals[account] = Decimal("0")
        if account not in credit_totals:
            credit_totals[account] = Decimal("0")

        # Per TR-4: tag the delta before affecting totals;
        # arithmetic is separated from the directional decision.
        if direction == "debit":
            debit_totals[account] = debit_totals[account] + amount
        else:  # direction == "credit"
            credit_totals[account] = credit_totals[account] + amount

    # Collect all known accounts across both accumulators
    all_accounts = set(debit_totals) | set(credit_totals)

    result: dict[str, dict] = {}
    for account in all_accounts:
        debit_value = debit_totals.get(account, Decimal("0"))
        credit_value = credit_totals.get(account, Decimal("0"))
        balance = credit_value - debit_value

        result[account] = {
            "debit": debit_value,
            "credit": credit_value,
            "balance": balance,
        }

    return result
