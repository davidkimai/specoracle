def build_user_purchase_index(
    events: list[dict],
    *,
    min_amount: int = 0,
) -> dict[str, dict[str, int]]:
    if min_amount < 0:
        raise ValueError("min_amount must be non-negative")
    result: dict[str, dict[str, int]] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        user_id = event.get("user_id")
        kind = event.get("kind")
        amount = event.get("amount")
        if (
            isinstance(user_id, str)
            and user_id
            and kind == "purchase"
            and isinstance(amount, int)
            and not isinstance(amount, bool)
            and amount >= min_amount
        ):
            if user_id not in result:
                result[user_id] = {"count": 0, "total": 0}
            result[user_id]["count"] += 1
            result[user_id]["total"] += amount
    return result
