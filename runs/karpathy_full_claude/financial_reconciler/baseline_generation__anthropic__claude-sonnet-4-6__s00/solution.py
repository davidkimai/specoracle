"""
financial_reconciler.py

Provides reconcile_entries for summarising debit/credit entries per account.
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
        Keyed by account name.  Each value is a dict with:
            - 'debit'   : total debits for the account
            - 'credit'  : total credits for the account
            - 'balance' : credit - debit

    Raises
    ------
    ValueError
        If any entry contains an unrecognised direction.
    KeyError
        If any entry is missing required fields.
    """
    VALID_DIRECTIONS = {"debit", "credit"}

    result: dict[str, dict[str, float]] = {}

    for idx, entry in enumerate(entries):
        # Validate required keys
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
                f"Must be one of {sorted(VALID_DIRECTIONS)}."
            )

        # Initialise account bucket if needed
        if account not in result:
            result[account] = {"debit": 0.0, "credit": 0.0, "balance": 0.0}

        result[account][direction] += amount

    # Compute balance for every account
    for account_data in result.values():
        account_data["balance"] = account_data["credit"] - account_data["debit"]

    return result
