from __future__ import annotations

from typing import Any


_REQUIRED_ITEM_KEYS = ("sku", "on_hand", "target", "case_pack")


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """Build a SKU-sorted reorder plan from inventory items and sales velocity."""
    if not isinstance(items, list):
        raise TypeError("items must be a list of dictionaries")
    if not isinstance(sales_velocity, dict):
        raise TypeError("sales_velocity must be a dictionary")

    _validate_sales_velocity(sales_velocity)

    plan = []
    for item in items:
        parsed = _parse_item(item)
        if parsed is None:
            continue

        sku, on_hand, target, case_pack = parsed
        if sales_velocity.get(sku, 0) <= 0:
            continue
        if on_hand >= target:
            continue

        deficit = target - on_hand
        reorder_quantity = _round_up_to_case_pack(deficit, case_pack)
        plan.append({"sku": sku, "reorder_quantity": reorder_quantity})

    return sorted(plan, key=lambda row: row["sku"])


def _parse_item(item: Any) -> tuple[str, int, int, int] | None:
    if not isinstance(item, dict):
        return None
    if any(key not in item for key in _REQUIRED_ITEM_KEYS):
        return None

    sku = item["sku"]
    on_hand = item["on_hand"]
    target = item["target"]
    case_pack = item["case_pack"]

    if not isinstance(sku, str):
        return None
    if not _is_plain_int(on_hand):
        return None
    if not _is_plain_int(target):
        return None
    if not _is_plain_int(case_pack):
        return None
    if case_pack <= 0:
        return None

    return sku, on_hand, target, case_pack


def _validate_sales_velocity(sales_velocity: dict[str, int]) -> None:
    for sku, velocity in sales_velocity.items():
        if not isinstance(sku, str):
            raise TypeError("sales_velocity keys must be strings")
        if not _is_plain_int(velocity):
            raise TypeError("sales_velocity values must be integers")


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _round_up_to_case_pack(quantity: int, case_pack: int) -> int:
    return ((quantity + case_pack - 1) // case_pack) * case_pack
