"""Financial entry reconciliation module."""

from __future__ import annotations


def reconcile_entries(entries: list[dict]) -> dict:
    """
    Reconcile financial entries by account.

    Each entry must contain:
      - "account": account identifier
      - "direction": either "debit" or "credit"
      - "amount": numeric amount

    Returns a dictionary keyed by account, with per-account totals:
      {
          account: {
              "debit": total_debits,
              "credit": total_credits,
              "balance": total_credits - total_debits,
          },
          ...
      }

    Raises:
        ValueError: If an entry has an unknown direction.
        KeyError: If a required entry field is missing.
    """
    reconciled: dict = {}

    for index, entry in enumerate(entries):
        account = entry["account"]
        direction = entry["direction"]
        amount = entry["amount"]

        if direction not in ("debit", "credit"):
            raise ValueError(f"unknown direction at entry {index}: {direction!r}")

        if account not in reconciled:
            reconciled[account] = {
                "debit": 0,
                "credit": 0,
                "balance": 0,
            }

        reconciled[account][direction] += amount

    for totals in reconciled.values():
        totals["balance"] = totals["credit"] - totals["debit"]

    return reconciled
