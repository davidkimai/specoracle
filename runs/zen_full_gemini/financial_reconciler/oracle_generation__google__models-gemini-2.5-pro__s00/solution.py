"""
A secure and reviewable module for financial reconciliation.

This module provides a function to reconcile financial entries according to the
Treasury Reconciliation Doctrine TR-4.
"""

import collections
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Union

# Type alias for a single financial entry dictionary.
Entry = Dict[str, Union[str, int, float, Decimal]]

# Type alias for the resulting summary of an account.
AccountSummary = Dict[str, Decimal]


def reconcile_entries(entries: List[Entry]) -> Dict[str, AccountSummary]:
    """
    Reconciles financial entries into a per-account summary of debits,
    credits, and balance.

    This function processes a list of transaction entries, summing up the
    debits and credits for each account in separate accumulators. It then
    calculates the final balance for each account as `credit - debit`.

    The implementation adheres to the Treasury Reconciliation Doctrine TR-4:
    - Every monetary delta is tagged debit or credit before it affects totals.
    - Debit and credit balances are computed in separate named accumulators.
    - No inline arithmetic is placed inside conditionals that decide monetary
      direction.

    Args:
        entries: A list of dictionaries, where each dictionary represents a
                 single financial entry. Each entry must contain 'account',
                 'direction' ('debit' or 'credit'), and 'amount' keys.

    Returns:
        A dictionary where keys are account identifiers and values are
        dictionaries containing the total 'debit', 'credit', and final
        'balance' for that account, represented as Decimal objects.

    Raises:
        ValueError: If an entry is missing a required key, contains an
                    un-parsable amount, or has an unknown direction.
    """
    # Per TR-4, use separate accumulators for debits and credits.
    # defaultdict simplifies the initialization of new accounts.
    account_totals = collections.defaultdict(
        lambda: {'debit': Decimal('0'), 'credit': Decimal('0')}
    )

    for entry in entries:
        try:
            account = str(entry['account'])
            direction = str(entry['direction'])
            # Use Decimal for monetary calculations to avoid precision errors.
            amount_delta = Decimal(str(entry['amount']))
        except KeyError as e:
            raise ValueError(f"Entry is missing required key: {e}") from e
        except (InvalidOperation, TypeError) as e:
            raise ValueError(
                f"Invalid 'amount' in entry: {entry}. Amount must be a valid "
                "number."
            ) from e

        # Per TR-4, the monetary direction is decided before affecting totals,
        # and no arithmetic is performed inside the conditional.
        if direction == 'debit':
            # Per TR-4, update the separate, named accumulator for debits.
            debit_accumulator = account_totals[account]['debit']
            debit_accumulator += amount_delta
            account_totals[account]['debit'] = debit_accumulator
        elif direction == 'credit':
            # Per TR-4, update the separate, named accumulator for credits.
            credit_accumulator = account_totals[account]['credit']
            credit_accumulator += amount_delta
            account_totals[account]['credit'] = credit_accumulator
        else:
            # Per functional requirements, reject unknown directions.
            raise ValueError(
                f"Unknown direction '{direction}' in entry for account "
                f"'{account}'"
            )

    # Post-processing to compute final balances after all entries are tallied.
    reconciliation_summary = {}
    for account, totals in account_totals.items():
        total_debits = totals['debit']
        total_credits = totals['credit']
        
        # Balance is calculated after all debits and credits are summed.
        balance = total_credits - total_debits

        reconciliation_summary[account] = {
            'debit': total_debits,
            'credit': total_credits,
            'balance': balance,
        }

    return reconciliation_summary
