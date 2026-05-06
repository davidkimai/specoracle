"""
financial_reconciler.py

Provides reconcile_entries() for per-account financial reconciliation.
"""

from __future__ import annotations


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile a list of financial entries per account.

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
        Keyed by account name.  Each value is a dict with:
            - 'debit'   : total debits
            - 'credit'  : total credits
            - 'balance' : credit - debit

    Raises
    ------
    ValueError
        If any entry contains an unknown direction (not 'debit' or 'credit').
    KeyError
        If any required field is missing from an entry.
    TypeError
        If 'amount' is not a numeric type.
    """
    VALID_DIRECTIONS = {"debit", "credit"}

    accounts: dict[str, dict[str, float]] = {}

    for idx, entry in enumerate(entries):
        # --- field presence validation ---
        for field in ("account", "direction", "amount"):
            if field not in entry:
                raise KeyError(
                    f"Entry at index {idx} is missing required field '{field}'."
                )

        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        # --- direction validation ---
        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Entry at index {idx} has unknown direction '{direction}'. "
                f"Allowed values are: {sorted(VALID_DIRECTIONS)}."
            )

        # --- amount type validation ---
        if not isinstance(amount, (int, float)):
            raise TypeError(
                f"Entry at index {idx} has a non-numeric amount: {amount!r}."
            )

        # --- accumulate ---
        if account not in accounts:
            accounts[account] = {"debit": 0.0, "credit": 0.0}

        accounts[account][direction] += float(amount)

    # --- compute balances ---
    result: dict[str, dict[str, float]] = {}
    for account, totals in accounts.items():
        debit = totals["debit"]
        credit = totals["credit"]
        result[account] = {
            "debit": debit,
            "credit": credit,
            "balance": credit - debit,
        }

    return result
