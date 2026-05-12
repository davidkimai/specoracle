def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Build a reorder plan for well-formed inventory items.

    A row is produced only when:
    - the item is a dict containing sku, on_hand, target, and case_pack;
    - sku is a str;
    - on_hand, target, and case_pack are ints;
    - case_pack is positive;
    - sales_velocity contains the sku with a positive int value;
    - on_hand is below target.

    The reorder quantity is the target deficit rounded up to a multiple of
    case_pack. Returned rows are sorted by sku.
    """
    if not isinstance(items, list) or not isinstance(sales_velocity, dict):
        return []

    plan: list[dict] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        sku = item.get("sku")
        on_hand = item.get("on_hand")
        target = item.get("target")
        case_pack = item.get("case_pack")

        if not isinstance(sku, str):
            continue
        if not (_is_int(on_hand) and _is_int(target) and _is_int(case_pack)):
            continue
        if case_pack <= 0:
            continue

        velocity = sales_velocity.get(sku)
        if not _is_int(velocity) or velocity <= 0:
            continue

        if on_hand >= target:
            continue

        deficit = target - on_hand
        reorder_quantity = ((deficit + case_pack - 1) // case_pack) * case_pack

        plan.append({"sku": sku, "reorder_quantity": reorder_quantity})

    return sorted(plan, key=lambda row: row["sku"])
