class _OmittedMinAmount(int):
    pass


_MIN_AMOUNT_OMITTED = _OmittedMinAmount(0)


def build_user_purchase_index(
    events: list[dict], *, min_amount: int = _MIN_AMOUNT_OMITTED
) -> dict[str, dict[str, int]]:
    if min_amount < 0:
        raise ValueError("min_amount must be non-negative")

    apply_min_amount = min_amount is not _MIN_AMOUNT_OMITTED

    index: dict[str, dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        if event.get("kind") != "purchase":
            continue

        user_id = event.get("user_id")
        if not isinstance(user_id, str) or user_id == "":
            continue

        amount = event.get("amount")
        if not isinstance(amount, int) or isinstance(amount, bool):
            continue

        if apply_min_amount and amount < min_amount:
            continue

        if user_id not in index:
            index[user_id] = {"count": 0, "total": 0}

        index[user_id]["count"] += 1
        index[user_id]["total"] += amount

    return index
