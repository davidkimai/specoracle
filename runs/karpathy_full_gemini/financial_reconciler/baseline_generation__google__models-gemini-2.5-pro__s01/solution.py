"""
A module for reconciling financial transaction entries.
"""

import collections
from typing import List, Dict, Union, Any

def reconcile_entries(entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Reconciles a list of financial entries into a per-account summary.

    This function processes a list of transactions, each represented by a
    dictionary. It aggregates the total debits and credits for each account
    and calculates the final balance.

    Args:
        entries: A list of dictionaries, where each dictionary represents a
                 financial entry. Each entry must contain the following keys:
                 - 'account' (str): The account identifier.
                 - 'direction' (str): The direction of the transaction, which
                   must be either 'debit' or 'credit'.
                 - 'amount' (int or float): The non-negative transaction amount.

    Returns:
        A dictionary where keys are account names. Each value is another
        dictionary containing the aggregated 'debit', 'credit', and the
        calculated 'balance' (credit - debit) for that account.

    Raises:
        TypeError: If the input 'entries' is not a list, if an item in the
                   list is not a dictionary, or if an 'amount' is not a
                   numeric type (int or float).
        ValueError: If an entry is malformed, such as missing a required key,
                    having an invalid 'direction', a negative 'amount', or an
                    empty 'account' name.
    """
    if not isinstance(entries, list):
        raise TypeError("Input 'entries' must be a list.")

    # Use a defaultdict to simplify aggregation.
    # The default value is a dictionary with debit and credit initialized to 0.0.
    reconciliation: collections.defaultdict = collections.defaultdict(
        lambda: {'debit': 0.0, 'credit': 0.0}
    )

    for i, entry in enumerate(entries):
        # --- Entry Validation ---
        if not isinstance(entry, dict):
            raise TypeError(f"Entry at index {i} must be a dictionary.")

        # Check for required keys
        required_keys = {'account', 'direction', 'amount'}
        if not required_keys.issubset(entry):
            missing_keys = required_keys - set(entry.keys())
            raise ValueError(
                f"Entry at index {i} is missing required keys: {', '.join(missing_keys)}"
            )

        # --- Value Extraction and Validation ---
        account = entry['account']
        direction = entry['direction']
        amount = entry['amount']

        if not isinstance(account, str) or not account.strip():
            raise ValueError(
                f"Entry at index {i}: 'account' must be a non-empty string."
            )
        # Normalize account name to handle leading/trailing whitespace
        account = account.strip()

        if direction not in ('debit', 'credit'):
            raise ValueError(
                f"Entry at index {i}: 'direction' must be 'debit' or 'credit', "
                f"not '{direction}'."
            )

        if not isinstance(amount, (int, float)):
            raise TypeError(
                f"Entry at index {i}: 'amount' must be a number (int or float)."
            )

        if amount < 0:
            raise ValueError(f"Entry at index {i}: 'amount' cannot be negative.")

        # --- Aggregation ---
        if direction == 'debit':
            reconciliation[account]['debit'] += float(amount)
        else:  # direction == 'credit'
            reconciliation[account]['credit'] += float(amount)

    # --- Final Calculation and Formatting ---
    final_result: Dict[str, Dict[str, float]] = {}
    for account, totals in reconciliation.items():
        debit = totals['debit']
        credit = totals['credit']
        final_result[account] = {
            'debit': debit,
            'credit': credit,
            'balance': credit - debit
        }

    return final_result
