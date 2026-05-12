"""
financial_reconciler.py

Provides reconcile_entries for summarising debit/credit ledger entries per account.
"""

from __future__ import annotations


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile a list of ledger entries.

    Parameters
    ----------
    entries : list[dict]
        Each entry must contain:
          - 'account'   : str  – account identifier
          - 'direction' : str  – 'debit' or 'credit'
          - 'amount'    : numeric – monetary amount (must be non-negative)

    Returns
    -------
    dict
        Keyed by account name.  Each value is a dict with:
          - 'debit'   : total debits
          - 'credit'  : total credits
          - 'balance' : credit - debit

    Raises
    ------
    ValueError
        If an entry contains an unknown direction (not 'debit' or 'credit'),
        a missing required key, or a negative amount.
    TypeError
        If 'amount' is not a numeric type.
    """
    VALID_DIRECTIONS = {"debit", "credit"}

    result: dict[str, dict[str, float]] = {}

    for index, entry in enumerate(entries):
        # Validate required keys
        for key in ("account", "direction", "amount"):
            if key not in entry:
                raise ValueError(
                    f"Entry at index {index} is missing required key '{key}'."
                )

        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        # Validate direction
        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Entry at index {index} has unknown direction '{direction}'. "
                f"Expected one of {sorted(VALID_DIRECTIONS)}."
            )

        # Validate amount type
        if not isinstance(amount, (int, float)):
            raise TypeError(
                f"Entry at index {index} has non-numeric amount '{amount}'."
            )

        # Validate amount sign
        if amount < 0:
            raise ValueError(
                f"Entry at index {index} has negative amount {amount}. "
                "Amounts must be non-negative."
            )

        # Initialise account bucket if needed
        if account not in result:
            result[account] = {"debit": 0.0, "credit": 0.0, "balance": 0.0}

        result[account][direction] += amount

    # Compute balance for every account
    for account_data in result.values():
        account_data["balance"] = account_data["credit"] - account_data["debit"]

    return result
