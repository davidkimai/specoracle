from typing import Any, Optional

__all__ = ["reorder_plan"]


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _parse_item(item: Any) -> Optional[tuple[str, int, int, int]]:
    if not isinstance(item, dict):
        return None

    sku = item.get("sku")
    on_hand = item.get("on_hand")
    target = item.get("target")
    case_pack = item.get("case_pack")

    if not isinstance(sku, str):
        return None
    if not _is_int(on_hand):
        return None
    if not _is_int(target):
        return None
    if not _is_int(case_pack):
        return None
    if case_pack <= 0:
        return None

    return sku, on_hand, target, case_pack


def _validate_sales_velocity(sales_velocity: Any) -> None:
    if not isinstance(sales_velocity, dict):
        raise TypeError("sales_velocity must be a dict")

    for sku, velocity in sales_velocity.items():
        if not isinstance(sku, str):
            raise TypeError("sales_velocity keys must be strings")
        if not _is_int(velocity):
            raise TypeError("sales_velocity values must be integers")


def _round_up_to_case_pack(quantity: int, case_pack: int) -> int:
    return ((quantity + case_pack - 1) // case_pack) * case_pack


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    _validate_sales_velocity(sales_velocity)

    rows: list[dict] = []

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
        rows.append({"sku": sku, "reorder_quantity": reorder_quantity})

    return sorted(rows, key=lambda row: row["sku"])
