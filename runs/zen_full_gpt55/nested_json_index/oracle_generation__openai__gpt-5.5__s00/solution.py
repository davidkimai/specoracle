__all__ = ["build_user_purchase_index"]


def _is_int(value: object) -> bool:
    return type(value) is int


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and value != ""


def _is_included_purchase(user_id: object, kind: object, amount: object) -> bool:
    return kind == "purchase" and _is_non_empty_string(user_id) and _is_int(amount)


def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    index: dict[str, dict[str, int]] = {}

    for position, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"events[{position}] must be a dictionary")

        user_id = event.get("user_id")
        kind = event.get("kind")
        amount = event.get("amount")

        if not _is_included_purchase(user_id, kind, amount):
            continue

        if user_id not in index:
            index[user_id] = {"count": 0, "total": 0}

        index[user_id]["count"] += 1
        index[user_id]["total"] += amount

    return index
