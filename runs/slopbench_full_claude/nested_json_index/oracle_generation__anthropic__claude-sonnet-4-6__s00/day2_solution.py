def build_user_purchase_index(events: list[dict], *, min_amount: int = 0) -> dict[str, dict[str, int]]:
    if min_amount < 0:
        raise ValueError("min_amount must be non-negative")
    index = {}
    for event in events:
        if event.get("kind") != "purchase":
            continue
        user_id = event.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            continue
        amount = event.get("amount")
        if not isinstance(amount, int):
            continue
        if amount < min_amount:
            continue
        if user_id not in index:
            index[user_id] = {"count": 0, "total": 0}
        index[user_id]["count"] += 1
        index[user_id]["total"] += amount
    return index
