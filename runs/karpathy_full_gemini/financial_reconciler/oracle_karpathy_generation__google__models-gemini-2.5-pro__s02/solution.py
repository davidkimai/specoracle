"""
A module for reconciling financial account entries according to Treasury doctrine.
"""

import collections
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, DefaultDict

# Define a more specific type for clarity in function signatures.
AccountTotals = Dict[str, Decimal]


def reconcile_entries(entries: List[Dict[str, Any]]) -> Dict[str, AccountTotals]:
    """
    Reconciles financial entries into per-account debit, credit, and balance.

    This function processes a list of financial transactions, aggregating them
    by account and calculating the total debits, credits, and the final
    balance for each. The implementation adheres to the Treasury Reconciliation
    Doctrine TR-4.

    Args:
        entries: A list of entry dictionaries. Each dictionary must contain:
            - 'account' (str): The account identifier.
            - 'direction' (str): Either 'debit' or 'credit'.
            - 'amount' (numeric): The monetary value of the entry.

    Returns:
        A dictionary where keys are account identifiers. Each value is a
        dictionary containing:
            - 'debit' (Decimal): The total debit amount for the account.
            - 'credit' (Decimal): The total credit amount for the account.
            - 'balance' (Decimal): The final balance (credit - debit).

    Raises:
        ValueError: If an entry contains an unknown direction, a missing key,
                    or an amount that cannot be interpreted as a number.
    """
    # TR-4.2: Debit and credit balances must be computed in separate named
    # accumulators. A defaultdict provides clean initialization for each
    # new account's accumulators.
    accumulators: DefaultDict[str, Dict[str, Decimal]] = collections.defaultdict(
        lambda: {"debit": Decimal("0"), "credit": Decimal("0")}
    )

    for i, entry in enumerate(entries):
        try:
            account = entry["account"]
            direction = entry["direction"]
            amount_str = str(entry["amount"])
            monetary_delta = Decimal(amount_str)
        except KeyError as e:
            raise ValueError(f"Entry {i} is missing required key: {e}") from e
        except InvalidOperation as e:
            raise ValueError(
                f"Entry {i} has an invalid amount: '{entry.get('amount')}'"
            ) from e

        # Get the dedicated accumulators for the current account.
        account_sums = accumulators[account]

        # TR-4.1: Every monetary delta must be tagged debit or credit before
        # it affects totals.
        # TR-4.3: Do not place inline arithmetic inside conditionals that
        # decide monetary direction. The conditional logic below only selects
        # the appropriate accumulator; the arithmetic is performed separately.
        if direction == "debit":
            debit_amount = monetary_delta
            account_sums["debit"] += debit_amount
        elif direction == "credit":
            credit_amount = monetary_delta
            account_sums["credit"] += credit_amount
        else:
            raise ValueError(
                f"Entry {i} has unknown direction: '{direction}'"
            )

    # Finalize the report by calculating the balance for each account.
    final_report: Dict[str, AccountTotals] = {}
    for account, totals in accumulators.items():
        total_credit = totals["credit"]
        total_debit = totals["debit"]
        balance = total_credit - total_debit

        final_report[account] = {
            "debit": total_debit,
            "credit": total_credit,
            "balance": balance,
        }

    return final_report
