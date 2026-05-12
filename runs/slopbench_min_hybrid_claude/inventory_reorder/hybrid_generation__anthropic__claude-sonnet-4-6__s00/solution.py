"""
inventory_reorder: compute a reorder plan given current inventory and sales velocity.
"""

import math

REQUIRED_KEYS = {"sku", "on_hand", "target", "case_pack"}


def _is_valid_item(item: dict) -> bool:
    if not isinstance(item, dict):
        return False
    if not REQUIRED_KEYS.issubset(item.keys()):
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


def _has_positive_velocity(sku: str, sales_velocity: dict) -> bool:
    velocity = sales_velocity.get(sku, 0)
    return isinstance(velocity, (int, float)) and velocity > 0


def _compute_reorder(item: dict, sales_velocity: dict):
    sku = str(item["sku"])
    on_hand = int(item["on_hand"])
    target = int(item["target"])
    case_pack = int(item["case_pack"])

    if case_pack <= 0:
        return None
    if not _has_positive_velocity(sku, sales_velocity):
        return None

    deficit = target - on_hand
    if deficit <= 0:
        return None

    reorder_quantity = _round_up_to_multiple(deficit, case_pack)
    return {"sku": sku, "reorder_quantity": reorder_quantity}


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not isinstance(sales_velocity, dict):
        raise TypeError("sales_velocity must be a dict")

    results = []
    for item in items:
        if not _is_valid_item(item):
            continue
        row = _compute_reorder(item, sales_velocity)
        if row is not None:
            results.append(row)

    results.sort(key=lambda row: row["sku"])
    return results
