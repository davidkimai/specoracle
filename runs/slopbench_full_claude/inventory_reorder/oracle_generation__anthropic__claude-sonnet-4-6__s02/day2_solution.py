"""
inventory_reorder: compute a reorder plan from inventory items and sales velocity.
"""

import math


REQUIRED_ITEM_KEYS = {"sku", "on_hand", "target", "case_pack"}


def _is_valid_item(item: dict) -> bool:
    if not isinstance(item, dict):
        return False
    if not REQUIRED_ITEM_KEYS.issubset(item.keys()):
        return False
    try:
        int(item["on_hand"])
        int(item["target"])
        int(item["case_pack"])
        str(item["sku"])
    except (TypeError, ValueError):
        return False
    return True


def _round_up_to_multiple(value: int, multiple: int) -> int:
    return math.ceil(value / multiple) * multiple


def reorder_plan(
    items: list[dict],
    sales_velocity: dict[str, int],
    include_days_of_cover: bool = False,
) -> list[dict]:
    plan = []

    for item in items:
        if not _is_valid_item(item):
            continue

        sku = str(item["sku"])
        on_hand = int(item["on_hand"])
        target = int(item["target"])
        case_pack = int(item["case_pack"])

        if case_pack <= 0:
            continue

        velocity = sales_velocity.get(sku, 0)
        if velocity <= 0:
            continue

        deficit = target - on_hand
        if deficit <= 0:
            continue

        reorder_quantity = _round_up_to_multiple(deficit, case_pack)
        row = {"sku": sku, "reorder_quantity": reorder_quantity}

        if include_days_of_cover:
            row["days_of_cover_before_reorder"] = on_hand // velocity

        plan.append(row)

    plan.sort(key=lambda row: row["sku"])
    return plan
