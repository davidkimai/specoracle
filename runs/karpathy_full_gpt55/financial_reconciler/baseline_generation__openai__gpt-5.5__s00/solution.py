from __future__ import annotations

from collections.abc import Hashable
from numbers import Number
from typing import Any


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile financial entries by account.

    Each entry must contain:
      - account: a hashable account identifier
      - direction: either "debit" or "credit"
      - amount: a numeric amount

    Returns a dictionary keyed by account. Each account value contains:
      - debit: total debit amount
      - credit: total credit amount
      - balance: credit - debit

    Raises:
        TypeError: if entries or entry fields have invalid types.
        KeyError: if a required entry key is missing.
        ValueError: if direction is not "debit" or "credit".
    """
    if not isinstance(entries, list):
        raise TypeError("entries must be a list of dictionaries")

    reconciled: dict[Any, dict[str, Any]] = {}

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise TypeError(f"entry at index {index} must be a dictionary")

        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        if not isinstance(account, Hashable):
            raise TypeError(f"account at index {index} must be hashable")

        if direction not in ("debit", "credit"):
            raise ValueError(
                f"unknown direction at index {index}: {direction!r}; "
                "expected 'debit' or 'credit'"
            )

        if isinstance(amount, bool) or not isinstance(amount, Number):
            raise TypeError(f"amount at index {index} must be numeric")

        if account not in reconciled:
            reconciled[account] = {"debit": 0, "credit": 0, "balance": 0}

        reconciled[account][direction] += amount

    for totals in reconciled.values():
        totals["balance"] = totals["credit"] - totals["debit"]

    return reconciled
