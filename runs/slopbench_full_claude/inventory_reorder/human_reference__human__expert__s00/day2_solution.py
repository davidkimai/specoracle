def reorder_plan(
    items: list[dict],
    sales_velocity: dict[str, int],
    include_days_of_cover: bool = False,
) -> list[dict]:
    rows = []
    for item in items:
        parsed = _parse_item(item)
        if parsed is None:
            continue
        sku, on_hand, target, case_pack = parsed
        velocity = sales_velocity.get(sku, 0)
        if velocity <= 0 or on_hand >= target:
            continue
        row = {
            "sku": sku,
            "reorder_quantity": _round_up_to_case(target - on_hand, case_pack),
        }
        if include_days_of_cover:
            row["days_of_cover_before_reorder"] = on_hand // velocity
        rows.append(row)
    return sorted(rows, key=lambda row: row["sku"])


def _parse_item(item: dict) -> tuple[str, int, int, int] | None:
    try:
        sku = item["sku"]
        on_hand = int(item["on_hand"])
        target = int(item["target"])
        case_pack = int(item["case_pack"])
    except (KeyError, TypeError, ValueError):
        return None
    if not sku or case_pack <= 0:
        return None
    return sku, on_hand, target, case_pack


def _round_up_to_case(deficit: int, case_pack: int) -> int:
    return ((deficit + case_pack - 1) // case_pack) * case_pack
