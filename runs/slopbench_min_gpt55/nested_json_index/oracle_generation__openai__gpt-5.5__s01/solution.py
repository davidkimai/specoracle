def _is_integer_amount(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and value != ""


def _is_purchase_event(event: dict) -> bool:
    return (
        event.get("kind") == "purchase"
        and _is_non_empty_string(event.get("user_id"))
        and _is_integer_amount(event.get("amount"))
    )


def _validate_events(events: list[dict]) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"events[{index}] must be a dictionary")


def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    _validate_events(events)

    index: dict[str, dict[str, int]] = {}

    for event in events:
        if not _is_purchase_event(event):
            continue

        user_id = event["user_id"]
        amount = event["amount"]

        if user_id not in index:
            index[user_id] = {"count": 0, "total": 0}

        index[user_id]["count"] += 1
        index[user_id]["total"] += amount

    return index
