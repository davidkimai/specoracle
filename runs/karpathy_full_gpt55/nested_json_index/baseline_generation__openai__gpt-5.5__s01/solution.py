from typing import Any


def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    index: dict[str, dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        user_id: Any = event.get("user_id")
        kind: Any = event.get("kind")
        amount: Any = event.get("amount")

        if kind != "purchase":
            continue
        if not isinstance(user_id, str) or user_id == "":
            continue
        if type(amount) is not int:
            continue

        if user_id not in index:
            index[user_id] = {"count": 0, "total": 0}

        index[user_id]["count"] += 1
        index[user_id]["total"] += amount

    return index
