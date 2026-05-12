# Standard library imports
import collections
from typing import Dict, List, Any, Union

# Define a more specific type for monetary values if desired.
# For this task, float or int will suffice.
Numeric = Union[int, float]

def reconcile_entries(
    entries: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Numeric]]:
    """
    Reconciles a list of financial entries into per-account totals.

    This function processes a list of transaction entries, where each entry is a
    dictionary containing an 'account', 'direction' ('debit' or 'credit'),
    and 'amount'. It aggregates the debits and credits for each account
    and calculates the final balance.

    The implementation adheres to the Treasury Reconciliation Doctrine TR-4:
    - Every monetary delta is tagged debit or credit before affecting totals.
    - Debit and credit balances are computed in separate named accumulators.
    - No inline arithmetic is placed inside conditionals that decide monetary
      direction.

    Args:
        entries: A list of entry dictionaries. Each dictionary must have
                 'account' (str), 'direction' (str), and 'amount' (Numeric)
                 keys.

    Returns:
        A dictionary where keys are account identifiers. Each value is
        another dictionary containing the total 'debit', total 'credit',
        and final 'balance' for that account.

    Raises:
        ValueError: If an entry contains a 'direction' other than 'debit'
                    or 'credit'.
        KeyError: If an entry is missing 'account', 'direction', or 'amount'.
    """
    # TR-4.2: Use separate named accumulators for debits and credits.
    # A defaultdict simplifies initialization of new accounts.
    account_totals: collections.defaultdict = collections.defaultdict(
        lambda: {'debit': 0.0, 'credit': 0.0}
    )

    for entry in entries:
        account = entry['account']
        direction = entry['direction']
        amount: Numeric = entry['amount']

        # TR-4.1: The monetary delta (amount) is tagged by 'direction'
        #         before it affects any total.
        # TR-4.3: The conditional logic is based on the direction tag, not
        #         on inline arithmetic.
        if direction == 'credit':
            account_totals[account]['credit'] += amount
        elif direction == 'debit':
            account_totals[account]['debit'] += amount
        else:
            raise ValueError(f"Unknown direction in entry: '{direction}'")

    # Final reconciliation: compute balances from the separate accumulators.
    final_reconciliation = {}
    for account, totals in account_totals.items():
        credit_total = totals['credit']
        debit_total = totals['debit']
        
        balance = credit_total - debit_total
        
        final_reconciliation[account] = {
            'debit': debit_total,
            'credit': credit_total,
            'balance': balance,
        }

    return final_reconciliation
