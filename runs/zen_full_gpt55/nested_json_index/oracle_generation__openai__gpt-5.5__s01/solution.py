def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and value != ""


def _is_integer(value: object) -> bool:
    return type(value) is int


def _validate_events(events: list[dict]) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"events[{index}] must be a dictionary")


def _is_countable_purchase(event: dict) -> bool:
    return (
        event.get("kind") == "purchase"
        and _is_non_empty_string(event.get("user_id"))
        and _is_integer(event.get("amount"))
    )


def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    _validate_events(events)

    purchase_index: dict[str, dict[str, int]] = {}

    for event in events:
        if not _is_countable_purchase(event):
            continue

        user_id = event["user_id"]
        amount = event["amount"]

        user_totals = purchase_index.get(user_id)
        if user_totals is None:
            purchase_index[user_id] = {"count": 1, "total": amount}
            continue

        user_totals["count"] += 1
        user_totals["total"] += amount

    return purchase_index
