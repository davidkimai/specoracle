PURCHASE_KIND = "purchase"


def _validate_events(events: object) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"events[{index}] must be a dictionary")


def _purchase_details(event: dict) -> tuple[str, int] | None:
    if event.get("kind") != PURCHASE_KIND:
        return None

    user_id = event.get("user_id")
    if not isinstance(user_id, str) or user_id == "":
        return None

    amount = event.get("amount")
    if type(amount) is not int:
        return None

    return user_id, amount


def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    _validate_events(events)

    purchase_index: dict[str, dict[str, int]] = {}

    for event in events:
        details = _purchase_details(event)
        if details is None:
            continue

        user_id, amount = details

        if user_id not in purchase_index:
            purchase_index[user_id] = {"count": 0, "total": 0}

        purchase_index[user_id]["count"] += 1
        purchase_index[user_id]["total"] += amount

    return purchase_index
