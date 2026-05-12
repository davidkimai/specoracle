"""
financial_reconciler.py

Provides reconcile_entries for summarising financial ledger entries per account.
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
            - 'amount'    : numeric – monetary amount

    Returns
    -------
    dict
        Keyed by account name. Each value is a dict with:
            - 'debit'   : total debits
            - 'credit'  : total credits
            - 'balance' : credit - debit

    Raises
    ------
    ValueError
        If an entry contains an unknown direction (not 'debit' or 'credit').
    KeyError
        If a required field is missing from an entry.
    """
    VALID_DIRECTIONS = {"debit", "credit"}

    summary: dict[str, dict[str, float]] = {}

    for idx, entry in enumerate(entries):
        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Entry {idx}: unknown direction '{direction}'. "
                f"Must be one of {sorted(VALID_DIRECTIONS)}."
            )

        if account not in summary:
            summary[account] = {"debit": 0.0, "credit": 0.0, "balance": 0.0}

        summary[account][direction] += amount

    # Compute balances after all entries are processed
    for account_data in summary.values():
        account_data["balance"] = account_data["credit"] - account_data["debit"]

    return summary
