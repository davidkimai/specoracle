from __future__ import annotations


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not isinstance(sales_velocity, dict):
        raise TypeError("sales_velocity must be a dict")

    rows: list[dict] = []

    for item in items:
        parsed_item = _parse_item(item)
        if parsed_item is None:
            continue

        sku, on_hand, target, case_pack = parsed_item

        if not _has_positive_velocity(sales_velocity, sku):
            continue
        if on_hand >= target:
            continue

        deficit = target - on_hand
        rows.append(
            {
                "sku": sku,
                "reorder_quantity": _round_up_to_case_pack(deficit, case_pack),
            }
        )

    return sorted(rows, key=lambda row: row["sku"])


def _parse_item(item: object) -> tuple[str, int, int, int] | None:
    if not isinstance(item, dict):
        return None

    try:
        sku = item["sku"]
        on_hand = item["on_hand"]
        target = item["target"]
        case_pack = item["case_pack"]
    except KeyError:
        return None

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


def _has_positive_velocity(sales_velocity: dict[str, int], sku: str) -> bool:
    velocity = sales_velocity.get(sku)
    return _is_plain_int(velocity) and velocity > 0


def _round_up_to_case_pack(quantity: int, case_pack: int) -> int:
    return ((quantity + case_pack - 1) // case_pack) * case_pack


def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
