from typing import Any

PurchaseIndex = dict[str, dict[str, int]]


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value != ""


def _is_integer_amount(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_events(events: Any) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"events[{index}] must be a dictionary")


def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    _validate_events(events)

    index: PurchaseIndex = {}

    for event in events:
        if event.get("kind") != "purchase":
            continue

        user_id = event.get("user_id")
        amount = event.get("amount")

        if not _is_non_empty_string(user_id):
            continue

        if not _is_integer_amount(amount):
            continue

        user_entry = index.setdefault(user_id, {"count": 0, "total": 0})
        user_entry["count"] += 1
        user_entry["total"] += amount

    return index
