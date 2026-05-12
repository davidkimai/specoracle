"""
A module for reconciling financial transaction entries.
"""

import collections
from typing import Any

__all__ = ['reconcile_entries']


def reconcile_entries(entries: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """
    Reconciles a list of financial entries into a per-account summary.

    This function processes a list of transaction entries, aggregates the total
    debits and credits for each account, and calculates the final balance.

    Args:
        entries: A list of dictionaries, where each dictionary represents a
                 financial entry. Each entry must contain the following keys:
                 - 'account' (str): The account identifier.
                 - 'direction' (str): The transaction direction, must be
                   'debit' or 'credit' (case-insensitive).
                 - 'amount' (int or float): The transaction amount, must be
                   non-negative.

    Returns:
        A dictionary where keys are account names and values are dictionaries
        containing the total 'debit', 'credit', and final 'balance' for
        each account. All monetary values are returned as floats.

    Raises:
        TypeError: If `entries` is not a list, an entry is not a dictionary,
                   or if any entry's values have incorrect types.
        KeyError: If an entry is missing a required key ('account', 'direction',
                  or 'amount').
        ValueError: If an entry has an unknown direction, a negative amount,
                    or an empty account name.
    """
    if not isinstance(entries, list):
        raise TypeError(f"Input must be a list of entries, not {type(entries).__name__}.")

    # The factory initializes a new account with zeroed debit and credit as floats.
    reconciliation = collections.defaultdict(lambda: {'debit': 0.0, 'credit': 0.0})

    for i, entry in enumerate(entries):
        # --- Entry Validation ---
        if not isinstance(entry, dict):
            raise TypeError(f"Entry at index {i} must be a dictionary, not {type(entry).__name__}.")

        try:
            account = entry['account']
            direction = entry['direction']
            amount = entry['amount']
        except KeyError as e:
            raise KeyError(f"Entry at index {i} is missing required key: {e}") from e

        # --- Type and Value Validation ---
        if not isinstance(account, str):
            raise TypeError(f"Key 'account' at index {i} must be a string, not {type(account).__name__}.")
        
        clean_account = account.strip()
        if not clean_account:
            raise ValueError(f"Key 'account' at index {i} cannot be empty or just whitespace.")

        if not isinstance(direction, str):
            raise TypeError(f"Key 'direction' at index {i} must be a string, not {type(direction).__name__}.")

        normalized_direction = direction.strip().lower()
        if normalized_direction not in ('debit', 'credit'):
            raise ValueError(
                f"Invalid direction '{direction}' at index {i}. Must be 'debit' or 'credit'."
            )

        if not isinstance(amount, (int, float)):
            raise TypeError(f"Key 'amount' at index {i} must be a number, not {type(amount).__name__}.")
        if amount < 0:
            raise ValueError(f"Amount '{amount}' at index {i} cannot be negative.")

        # --- Aggregation ---
        reconciliation[clean_account][normalized_direction] += float(amount)

    # --- Final Balance Calculation ---
    result = {}
    for account, data in reconciliation.items():
        credit = data['credit']
        debit = data['debit']
        result[account] = {
            'credit': credit,
            'debit': debit,
            'balance': credit - debit,
        }

    return result
