"""
financial_reconciler.py

Provides reconcile_entries to aggregate debit/credit entries per account
and compute balances.
"""

from __future__ import annotations


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile a list of financial entries.

    Parameters
    ----------
    entries : list[dict]
        Each entry must contain:
          - 'account'   : str  – account identifier
          - 'direction' : str  – 'debit' or 'credit'
          - 'amount'    : numeric – transaction amount

    Returns
    -------
    dict
        Mapping of account -> {'debit': float, 'credit': float, 'balance': float}
        where balance = credit - debit.

    Raises
    ------
    ValueError
        If any entry contains an unknown direction (not 'debit' or 'credit').
    KeyError
        If any entry is missing a required field.
    TypeError
        If amount is not numeric.
    """
    VALID_DIRECTIONS = {"debit", "credit"}

    result: dict[str, dict[str, float]] = {}

    for idx, entry in enumerate(entries):
        # Validate required fields
        for field in ("account", "direction", "amount"):
            if field not in entry:
                raise KeyError(
                    f"Entry at index {idx} is missing required field '{field}'."
                )

        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        # Validate direction
        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Entry at index {idx} has unknown direction '{direction}'. "
                f"Expected one of {sorted(VALID_DIRECTIONS)}."
            )

        # Validate amount is numeric
        if not isinstance(amount, (int, float)):
            raise TypeError(
                f"Entry at index {idx} has non-numeric amount '{amount}'."
            )

        # Initialise account bucket if necessary
        if account not in result:
            result[account] = {"debit": 0.0, "credit": 0.0, "balance": 0.0}

        result[account][direction] += float(amount)

    # Compute balances
    for account, totals in result.items():
        totals["balance"] = totals["credit"] - totals["debit"]

    return result
