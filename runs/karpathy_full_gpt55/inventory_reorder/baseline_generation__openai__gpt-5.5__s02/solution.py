"""Inventory reorder planning module."""

from typing import Any


def _is_int_not_bool(value: Any) -> bool:
    """Return True when value is an int but not a bool."""
    return isinstance(value, int) and not isinstance(value, bool)


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Build a reorder plan for inventory items.

    Malformed items are skipped. Items are reordered only when:
    - sku is present and is a string,
    - on_hand, target, and case_pack are integers,
    - case_pack is positive,
    - sales_velocity for the sku is present and positive,
    - on_hand is below target.

    Reorder quantities are rounded up to the nearest multiple of case_pack.
    """
    if not isinstance(items, list):
        return []

    velocity_by_sku = sales_velocity if isinstance(sales_velocity, dict) else {}
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
        if not (
            _is_int_not_bool(on_hand)
            and _is_int_not_bool(target)
            and _is_int_not_bool(case_pack)
        ):
            continue
        if case_pack <= 0:
            continue

        velocity = velocity_by_sku.get(sku)
        if not _is_int_not_bool(velocity) or velocity <= 0:
            continue

        if on_hand >= target:
            continue

        deficit = target - on_hand
        reorder_quantity = ((deficit + case_pack - 1) // case_pack) * case_pack

        plan.append({"sku": sku, "reorder_quantity": reorder_quantity})

    plan.sort(key=lambda row: row["sku"])
    return plan
