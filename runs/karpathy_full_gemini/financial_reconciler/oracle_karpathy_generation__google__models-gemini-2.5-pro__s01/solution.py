#
# Copyright (c) 2023, Independent Security Evaluators, LLC
#
# All rights reserved.
#
"""
A module for financial reconciliation of debit and credit entries, adhering to
the Treasury Reconciliation Doctrine TR-4.
"""

import collections
from typing import Dict, List, Union


def reconcile_entries(entries: List[Dict]) -> Dict[str, Dict[str, Union[int, float]]]:
    """
    Reconciles a list of financial entries into per-account totals.

    This function processes a list of transaction entries, each specifying an
    account, a direction (debit or credit), and an amount. It aggregates these
    entries to compute the total debit, total credit, and final balance for
    each account.

    The implementation adheres to the Treasury Reconciliation Doctrine TR-4:
    - Every monetary delta is tagged as debit or credit before affecting totals.
    - Debit and credit balances are computed in separate named accumulators.
    - No inline arithmetic is placed inside conditionals that decide monetary
      direction.

    Args:
        entries: A list of dictionaries, where each dictionary represents a
                 single financial entry with 'account', 'direction', and
                 'amount' keys.

    Returns:
        A dictionary where keys are account names and values are dictionaries
        containing the total 'debit', 'credit', and final 'balance' for that
        account.

    Raises:
        ValueError: If an entry contains a direction other than 'debit' or 'credit'.
        KeyError: If an entry is missing 'account', 'direction', or 'amount'.
    """
    # Per-account accumulators for debit and credit totals, satisfying TR-4.
    # Using defaultdict simplifies the initialization of new accounts.
    account_summaries = collections.defaultdict(
        lambda: {'debit': 0, 'credit': 0}
    )

    for entry in entries:
        account = entry['account']
        direction = entry['direction']
        amount = entry['amount']

        # TR-4: Tag monetary delta by direction before affecting totals.
        # The conditional is free of inline arithmetic.
        if direction == 'debit':
            # TR-4: Update separate named accumulator for debits.
            account_summaries[account]['debit'] += amount
        elif direction == 'credit':
            # TR-4: Update separate named accumulator for credits.
            account_summaries[account]['credit'] += amount
        else:
            raise ValueError(f"Unknown direction: '{direction}' in entry: {entry}")

    # Finalize the results by calculating the balance for each account.
    final_reconciliation = {}
    for account, totals in account_summaries.items():
        debit_total = totals['debit']
        credit_total = totals['credit']
        
        # Balance is calculated after all entries are processed.
        balance = credit_total - debit_total

        final_reconciliation[account] = {
            'debit': debit_total,
            'credit': credit_total,
            'balance': balance,
        }

    return final_reconciliation
