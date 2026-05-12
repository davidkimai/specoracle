def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    rows: list[dict] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        sku = item.get("sku")
        on_hand = item.get("on_hand")
        target = item.get("target")
        case_pack = item.get("case_pack")

        if not isinstance(sku, str):
            continue
        if not (_is_int(on_hand) and _is_int(target) and _is_int(case_pack)):
            continue
        if case_pack <= 0:
            continue

        velocity = sales_velocity.get(sku)
        if not _is_int(velocity) or velocity <= 0:
            continue

        if on_hand >= target:
            continue

        deficit = target - on_hand
        reorder_quantity = ((deficit + case_pack - 1) // case_pack) * case_pack
        rows.append({"sku": sku, "reorder_quantity": reorder_quantity})

    return sorted(rows, key=lambda row: row["sku"])
