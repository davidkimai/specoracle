import math


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Compute a reorder plan for inventory items.

    Parameters
    ----------
    items : list[dict]
        Each element should contain 'sku', 'on_hand', 'target', and 'case_pack'.
    sales_velocity : dict[str, int]
        Maps SKU to the number of units sold per period.

    Returns
    -------
    list[dict]
        Sorted list of {"sku": str, "reorder_quantity": int} for items that
        need reordering.
    """
    required_keys = {"sku", "on_hand", "target", "case_pack"}
    results = []

    for item in items:
        # Skip malformed items (missing required keys or wrong types)
        if not isinstance(item, dict):
            continue
        if not required_keys.issubset(item.keys()):
            continue

        sku = item["sku"]
        on_hand = item["on_hand"]
        target = item["target"]
        case_pack = item["case_pack"]

        # Validate types: sku must be a string, numeric fields must be numeric
        if not isinstance(sku, str):
            continue
        if not isinstance(on_hand, (int, float)) or isinstance(on_hand, bool):
            continue
        if not isinstance(target, (int, float)) or isinstance(target, bool):
            continue
        if not isinstance(case_pack, (int, float)) or isinstance(case_pack, bool):
            continue

        # Skip non-positive case_pack
        if case_pack <= 0:
            continue

        # Skip if sales velocity is absent or non-positive
        velocity = sales_velocity.get(sku)
        if velocity is None or not isinstance(velocity, (int, float)) or isinstance(velocity, bool):
            continue
        if velocity <= 0:
            continue

        # Only reorder when on_hand is below target
        deficit = target - on_hand
        if deficit <= 0:
            continue

        # Round up deficit to the nearest multiple of case_pack
        reorder_quantity = int(math.ceil(deficit / case_pack) * case_pack)

        results.append({"sku": sku, "reorder_quantity": reorder_quantity})

    # Sort by sku
    results.sort(key=lambda x: x["sku"])
    return results
