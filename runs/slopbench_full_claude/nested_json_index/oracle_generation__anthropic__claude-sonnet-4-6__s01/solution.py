def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    index: dict[str, dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("kind") != "purchase":
            continue
        user_id = event.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            continue
        amount = event.get("amount")
        if not isinstance(amount, int) or isinstance(amount, bool):
            continue

        if user_id not in index:
            index[user_id] = {"count": 0, "total": 0}
        index[user_id]["count"] += 1
        index[user_id]["total"] += amount

    return index
