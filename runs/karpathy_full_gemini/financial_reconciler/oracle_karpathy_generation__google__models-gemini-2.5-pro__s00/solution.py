# financial_reconciler.py

"""
A module for reconciling financial transaction entries according to Treasury
Reconciliation Doctrine TR-4.
"""

from collections import defaultdict
from typing import Dict, List, Union

# Type aliases for clarity
Numeric = Union[int, float]
Entry = Dict[str, Union[str, Numeric]]
AccountTotals = Dict[str, Numeric]
ReconciliationResult = Dict[str, AccountTotals]


class ReconciliationError(ValueError):
    """Custom exception for failures during the reconciliation process."""
    pass


def reconcile_entries(entries: List[Entry]) -> ReconciliationResult:
    """
    Reconciles a list of financial entries into per-account summaries.

    This function processes a list of transaction entries, aggregating them by
    account. It adheres to the Treasury Reconciliation Doctrine TR-4, which
    mandates separate accumulation for debits and credits and a clear separation
    between decision logic and arithmetic operations.

    Args:
        entries: A list of entry dictionaries. Each dictionary must contain:
                 - 'account' (str): The account identifier.
                 - 'direction' (str): The transaction direction, either
                   'debit' or 'credit'.
                 - 'amount' (int or float): The monetary value of the transaction.

    Returns:
        A dictionary where keys are account identifiers. Each value is another
        dictionary containing the total 'debit', total 'credit', and final
        'balance' (credit - debit) for that account.

    Raises:
        ReconciliationError: If an entry is malformed (e.g., missing keys,
                             invalid amount) or contains an unknown direction.
    """
    # TR-4: Debit and credit balances must be computed in separate named accumulators.
    # We initialize separate 'debit' and 'credit' accumulators for each account.
    account_accumulators = defaultdict(lambda: {"debit": 0.0, "credit": 0.0})

    for i, entry in enumerate(entries):
        try:
            account = str(entry["account"])
            direction = str(entry["direction"])
            amount = float(entry["amount"])
        except (KeyError, TypeError, ValueError) as e:
            raise ReconciliationError(
                f"Invalid format in entry at index {i}: {entry}"
            ) from e

        debit_delta = 0.0
        credit_delta = 0.0

        # TR-4: Do not place inline arithmetic inside conditionals that decide monetary direction.
        # This conditional block's sole responsibility is to determine the monetary
        # direction and assign the amount to the correct temporary delta variable.
        if direction == "credit":
            credit_delta = amount
        elif direction == "debit":
            debit_delta = amount
        else:
            raise ReconciliationError(
                f"Unknown direction '{direction}' in entry at index {i}: {entry}"
            )

        # TR-4: Every monetary delta must be tagged debit or credit before it affects totals.
        # The 'debit_delta' and 'credit_delta' variables serve as these tags.
        # The arithmetic to update the totals occurs here, separate from the decision logic.
        account_accumulators[account]["debit"] += debit_delta
        account_accumulators[account]["credit"] += credit_delta

    # Finalize the result by calculating the balance for each account.
    final_report: ReconciliationResult = {}
    for account, totals in account_accumulators.items():
        debit_total = totals["debit"]
        credit_total = totals["credit"]
        balance = credit_total - debit_total

        final_report[account] = {
            "debit": debit_total,
            "credit": credit_total,
            "balance": balance,
        }

    return final_report
