def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    index: dict[str, dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        if kind != "purchase":
            continue
        if not isinstance(user_id, str) or not user_id:
            continue
        if not isinstance(amount, int) or isinstance(amount, bool):
            continue

        if user_id not in index:
            index[user_id] = {"count": 0, "total": 0}

        index[user_id]["count"] += 1
        index[user_id]["total"] += amount

    return index
