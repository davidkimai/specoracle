"""
A module for reconciling financial transaction entries.
"""

import collections
import numbers
from typing import Any


def reconcile_entries(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Reconciles a list of financial entries into a per-account summary.

    This function processes a list of transactions, aggregates the total debits
    and credits for each account, and calculates the final balance.

    Args:
        entries: A list of dictionaries, where each dictionary represents a
                 financial entry with 'account' (str), 'direction' (str,
                 'debit' or 'credit'), and 'amount' (numeric) keys.

    Returns:
        A dictionary where keys are account names and values are dictionaries
        containing the total 'debit', 'credit', and calculated 'balance'
        (credit - debit) for that account.

    Raises:
        KeyError: If an entry is missing a required key ('account',
                  'direction', 'amount').
        TypeError: If 'account' is not a string or 'amount' is not a number.
        ValueError: If an entry has an invalid 'direction' (not 'debit' or
                    'credit'), an empty 'account' string, or if 'amount'
                    is negative.
    """
    reconciliation = collections.defaultdict(lambda: {"debit": 0, "credit": 0})

    for i, entry in enumerate(entries):
        try:
            account = entry["account"]
            direction = entry["direction"]
            amount = entry["amount"]
        except KeyError as e:
            raise KeyError(
                f"Entry at index {i} is missing required key: {e}"
            ) from e

        if not isinstance(account, str):
            raise TypeError(
                f"Entry at index {i}: 'account' must be a string, "
                f"not {type(account).__name__}."
            )
        if not account:
            raise ValueError(f"Entry at index {i}: 'account' cannot be empty.")

        if direction not in ("debit", "credit"):
            raise ValueError(
                f"Entry at index {i}: Invalid 'direction' value '{direction}'. "
                "Must be 'debit' or 'credit'."
            )

        if not isinstance(amount, numbers.Number):
            raise TypeError(
                f"Entry at index {i}: 'amount' must be a number, "
                f"not {type(amount).__name__}."
            )
        if amount < 0:
            raise ValueError(
                f"Entry at index {i}: 'amount' cannot be negative: {amount}."
            )

        reconciliation[account][direction] += amount

    result = {}
    for account, summary in reconciliation.items():
        balance = summary["credit"] - summary["debit"]
        result[account] = {
            "debit": summary["debit"],
            "credit": summary["credit"],
            "balance": balance,
        }

    return result
