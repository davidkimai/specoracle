#
# Copyright (c) 2024, Resource Synthesis Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""
financial_reconciler provides a function to reconcile financial entries
according to Treasury Reconciliation Doctrine TR-4.
"""

import collections
from typing import Dict, List, Any, Union

# Type definitions for clarity.
Numeric = Union[int, float]
Entry = Dict[str, Any]
AccountSummary = Dict[str, Numeric]
ReconciliationResult = Dict[Any, AccountSummary]


def reconcile_entries(entries: List[Entry]) -> ReconciliationResult:
    """
    Reconciles a list of financial entries into per-account summaries.

    This function processes a list of transaction entries, aggregates them by
    account, and calculates the total debits, credits, and final balance for
    each account. It strictly adheres to Treasury Reconciliation Doctrine TR-4.

    Args:
        entries: A list of dictionaries, where each dictionary represents a
                 financial transaction with 'account', 'direction' ('debit' or
                 'credit'), and 'amount' keys.

    Returns:
        A dictionary where keys are account identifiers and values are
        dictionaries containing the total 'debit', 'credit', and final
        'balance' for that account.

    Raises:
        ValueError: If an entry contains a 'direction' other than 'debit' or
                    'credit'.
        KeyError: If an entry is missing 'account', 'direction', or 'amount'.
    """
    # Per TR-4, debit and credit balances must be computed in separate named
    # accumulators. A defaultdict initializes these accumulators to zero for
    # each new account encountered.
    account_totals = collections.defaultdict(
        lambda: {"debit": 0, "credit": 0}
    )

    for entry in entries:
        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        # Per TR-4, every monetary delta must be tagged debit or credit before
        # it affects totals. The conditional block below enforces this by
        # routing the amount based on the 'direction' tag.
        #
        # Per TR-4, do not place inline arithmetic inside conditionals that
        # decide monetary direction. The conditions below are simple string
        # comparisons, and the arithmetic is performed inside the block.
        if direction == "debit":
            debit_delta = amount
            account_totals[account]["debit"] += debit_delta
        elif direction == "credit":
            credit_delta = amount
            account_totals[account]["credit"] += credit_delta
        else:
            raise ValueError(
                f"Invalid direction '{direction}' in entry for account "
                f"'{account}'. Must be 'debit' or 'credit'."
            )

    # The final reconciliation result is constructed after all entries have
    # been processed and accumulated.
    result: ReconciliationResult = {}
    for account, totals in account_totals.items():
        debit_total = totals["debit"]
        credit_total = totals["credit"]
        balance = credit_total - debit_total

        result[account] = {
            "debit": debit_total,
            "credit": credit_total,
            "balance": balance,
        }

    return result
