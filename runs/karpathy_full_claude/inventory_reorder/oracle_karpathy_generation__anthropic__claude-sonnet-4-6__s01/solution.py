import math


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    result = []
    for item in items:
        try:
            sku = item["sku"]
            on_hand = item["on_hand"]
            target = item["target"]
            case_pack = item["case_pack"]
        except (KeyError, TypeError):
            continue

        if not isinstance(case_pack, (int, float)) or case_pack <= 0:
            continue

        velocity = sales_velocity.get(sku, 0)
        if velocity <= 0:
            continue

        if on_hand < target:
            deficit = target - on_hand
            reorder_quantity = math.ceil(deficit / case_pack) * case_pack
            result.append({"sku": sku, "reorder_quantity": int(reorder_quantity)})

    result.sort(key=lambda x: x["sku"])
    return result
