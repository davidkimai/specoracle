def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        user_id = event.get("user_id")
        kind = event.get("kind")
        amount = event.get("amount")
        if (
            kind == "purchase"
            and isinstance(user_id, str)
            and user_id
            and isinstance(amount, int)
            and not isinstance(amount, bool)
        ):
            if user_id not in result:
                result[user_id] = {"count": 0, "total": 0}
            result[user_id]["count"] += 1
            result[user_id]["total"] += amount
    return result
