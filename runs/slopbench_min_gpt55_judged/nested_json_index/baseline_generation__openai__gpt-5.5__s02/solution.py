from __future__ import annotations


def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    """
    Build an index of purchase counts and totals per user.

    Only events with:
    - kind == "purchase"
    - user_id as a non-empty string
    - amount as an integer, excluding bool
    are included.
    """
    index: dict[str, dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        user_id = event.get("user_id")
        if not isinstance(user_id, str) or user_id == "":
            continue

        if event.get("kind") != "purchase":
            continue

        amount = event.get("amount")
        if not isinstance(amount, int) or isinstance(amount, bool):
            continue

        user_entry = index.setdefault(user_id, {"count": 0, "total": 0})
        user_entry["count"] += 1
        user_entry["total"] += amount

    return index
