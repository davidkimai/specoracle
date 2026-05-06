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
        if kind != "purchase":
            continue
        if not isinstance(user_id, str) or not user_id:
            continue
        if not isinstance(amount, int) or isinstance(amount, bool):
            continue
        if amount < min_amount:
            continue
        if user_id not in result:
            result[user_id] = {"count": 0, "total": 0}
        result[user_id]["count"] += 1
        result[user_id]["total"] += amount
    return result
