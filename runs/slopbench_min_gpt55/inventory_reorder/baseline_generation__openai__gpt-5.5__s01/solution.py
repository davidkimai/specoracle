from __future__ import annotations

from typing import Any


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Build a reorder plan for valid inventory items.

    Malformed items are skipped. An item is considered valid when it is a dict
    containing:
      - sku: str
      - on_hand: int
      - target: int
      - case_pack: positive int

    Items are reordered only when their sales velocity is present and positive,
    and on_hand is below target.
    """
    if not isinstance(items, list):
        return []

    velocities = sales_velocity if isinstance(sales_velocity, dict) else {}
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
        if not _is_int(on_hand) or not _is_int(target) or not _is_int(case_pack):
            continue
        if case_pack <= 0:
            continue

        velocity = velocities.get(sku)
        if not _is_int(velocity) or velocity <= 0:
            continue

        if on_hand >= target:
            continue

        deficit = target - on_hand
        reorder_quantity = ((deficit + case_pack - 1) // case_pack) * case_pack

        plan.append({"sku": sku, "reorder_quantity": reorder_quantity})

    plan.sort(key=lambda row: row["sku"])
    return plan
