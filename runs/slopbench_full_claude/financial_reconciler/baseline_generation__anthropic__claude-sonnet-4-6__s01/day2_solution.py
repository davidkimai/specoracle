"""
financial_reconciler.py

Provides reconcile_entries for summarising financial journal entries
per account, computing per-account debit totals, credit totals, and
balance (credit - debit).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable


def reconcile_entries(
    entries: list[dict],
    include_zero_accounts: Iterable[str] | None = None,
) -> dict:
    """
    Reconcile a list of journal entries.

    Parameters
    ----------
    entries : list[dict]
        Each entry must contain:
          - 'account'   : str  – account identifier
          - 'direction' : str  – either 'debit' or 'credit'
          - 'amount'    : numeric – monetary amount (must be non-negative)
    include_zero_accounts : iterable[str] | None
        Optional collection of account names that must appear in the result
        with zero debit, credit, and balance even when no entries reference
        them.  Accounts that do have entries are unaffected.

    Returns
    -------
    dict
        Keyed by account name; each value is a dict with:
          - 'debit'   : Decimal – total debits
          - 'credit'  : Decimal – total credits
          - 'balance' : Decimal – credit minus debit

    Raises
    ------
    ValueError
        If an entry contains an unknown direction, a missing required field,
        or a negative amount.
    TypeError
        If 'entries' is not a list, or an individual entry is not a dict.
    """
    if not isinstance(entries, list):
        raise TypeError(f"entries must be a list, got {type(entries).__name__!r}")

    VALID_DIRECTIONS = {"debit", "credit"}
    ZERO = Decimal("0")
    accounts: dict[str, dict[str, Decimal]] = {}

    # Pre-populate zero accounts before processing entries so that entries
    # for those accounts still accumulate correctly.
    if include_zero_accounts is not None:
        for name in include_zero_accounts:
            if not isinstance(name, str) or not name:
                raise ValueError(
                    "include_zero_accounts must contain non-empty strings; "
                    f"got {name!r}"
                )
            if name not in accounts:
                accounts[name] = {"debit": ZERO, "credit": ZERO}

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise TypeError(
                f"Entry at index {index} must be a dict, got {type(entry).__name__!r}"
            )

        # Validate required fields
        for field in ("account", "direction", "amount"):
            if field not in entry:
                raise ValueError(
                    f"Entry at index {index} is missing required field {field!r}"
                )

        account: Any = entry["account"]
        direction: Any = entry["direction"]
        amount: Any = entry["amount"]

        if not isinstance(account, str) or not account:
            raise ValueError(
                f"Entry at index {index}: 'account' must be a non-empty string"
            )

        if not isinstance(direction, str) or direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"Entry at index {index}: unknown direction {direction!r}; "
                f"must be one of {sorted(VALID_DIRECTIONS)}"
            )

        try:
            amount_decimal = Decimal(str(amount))
        except Exception as exc:
            raise ValueError(
                f"Entry at index {index}: 'amount' could not be converted to Decimal: {exc}"
            ) from exc

        if amount_decimal < ZERO:
            raise ValueError(
                f"Entry at index {index}: 'amount' must be non-negative, got {amount_decimal}"
            )

        if account not in accounts:
            accounts[account] = {"debit": ZERO, "credit": ZERO}

        accounts[account][direction] += amount_decimal

    # Build final result with balance
    result: dict[str, dict[str, Decimal]] = {}
    for account, totals in accounts.items():
        debit = totals["debit"]
        credit = totals["credit"]
        result[account] = {
            "debit": debit,
            "credit": credit,
            "balance": credit - debit,
        }

    return result
