def _is_valid_purchase(event: dict) -> bool:
    if event.get("kind") != "purchase":
        return False
    user_id = event.get("user_id")
    if not isinstance(user_id, str) or not user_id:
        return False
    return isinstance(event.get("amount"), int)


def _accumulate(index: dict[str, dict[str, int]], user_id: str, amount: int) -> None:
    if user_id not in index:
        index[user_id] = {"count": 0, "total": 0}
    index[user_id]["count"] += 1
    index[user_id]["total"] += amount


def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    index: dict[str, dict[str, int]] = {}
    for event in events:
        if _is_valid_purchase(event):
            _accumulate(index, event["user_id"], event["amount"])
    return index
