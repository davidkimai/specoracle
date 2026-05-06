"""
inventory_reorder: compute reorder quantities for inventory items.
"""

import math


REQUIRED_KEYS = {"sku", "on_hand", "target", "case_pack"}


def _is_valid_item(item: dict) -> bool:
    if not isinstance(item, dict):
        return False
    if not REQUIRED_KEYS.issubset(item):
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


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Compute reorder quantities for items that are below target and have
    positive sales velocity.

    Args:
        items: list of item dicts with keys sku, on_hand, target, case_pack.
        sales_velocity: mapping of sku to sales velocity (int).

    Returns:
        Sorted list of dicts with keys sku and reorder_quantity.
    """
    result = []

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
        if not isinstance(velocity, int):
            try:
                velocity = int(velocity)
            except (TypeError, ValueError):
                continue

        if velocity <= 0:
            continue

        deficit = target - on_hand
        if deficit <= 0:
            continue

        reorder_quantity = _round_up_to_multiple(deficit, case_pack)
        result.append({"sku": sku, "reorder_quantity": reorder_quantity})

    result.sort(key=lambda row: row["sku"])
    return result
