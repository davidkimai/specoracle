def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    rows = []

    for item in items:
        if not isinstance(item, dict):
            continue

        sku = item.get("sku")
        on_hand = item.get("on_hand")
        target = item.get("target")
        case_pack = item.get("case_pack")

        if not isinstance(sku, str):
            continue
        if type(on_hand) is not int or type(target) is not int or type(case_pack) is not int:
            continue
        if case_pack <= 0:
            continue

        velocity = sales_velocity.get(sku)
        if type(velocity) is not int or velocity <= 0:
            continue

        if on_hand < target:
            deficit = target - on_hand
            reorder_quantity = ((deficit + case_pack - 1) // case_pack) * case_pack
            rows.append({"sku": sku, "reorder_quantity": reorder_quantity})

    return sorted(rows, key=lambda row: row["sku"])
