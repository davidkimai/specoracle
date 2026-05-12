from __future__ import annotations

from collections.abc import Mapping
from typing import Any


_REQUIRED_ITEM_KEYS = {"sku", "on_hand", "target", "case_pack"}


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not isinstance(sales_velocity, Mapping):
        raise TypeError("sales_velocity must be a mapping")

    rows: list[dict] = []

    for item in items:
        parsed = _parse_item(item)
        if parsed is None:
            continue

        sku, on_hand, target, case_pack = parsed
        velocity = sales_velocity.get(sku, 0)

        if not _is_int(velocity):
            raise TypeError(f"sales_velocity for sku {sku!r} must be an int")
        if velocity <= 0:
            continue
        if on_hand >= target:
            continue

        deficit = target - on_hand
        reorder_quantity = _round_up_to_case_pack(deficit, case_pack)
        rows.append({"sku": sku, "reorder_quantity": reorder_quantity})

    return sorted(rows, key=lambda row: row["sku"])


def _parse_item(item: Any) -> tuple[str, int, int, int] | None:
    if not isinstance(item, Mapping):
        return None
    if not _REQUIRED_ITEM_KEYS.issubset(item):
        return None

    sku = item["sku"]
    on_hand = item["on_hand"]
    target = item["target"]
    case_pack = item["case_pack"]

    if not isinstance(sku, str):
        return None
    if not _is_int(on_hand) or not _is_int(target) or not _is_int(case_pack):
        return None
    if case_pack <= 0:
        return None

    return sku, on_hand, target, case_pack


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _round_up_to_case_pack(quantity: int, case_pack: int) -> int:
    return ((quantity + case_pack - 1) // case_pack) * case_pack
