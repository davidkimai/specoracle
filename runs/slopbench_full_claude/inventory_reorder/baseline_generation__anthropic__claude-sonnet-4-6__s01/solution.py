import math


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Compute a reorder plan for inventory items.

    Parameters
    ----------
    items : list[dict]
        Each element should contain keys: sku, on_hand, target, case_pack.
    sales_velocity : dict[str, int]
        Maps sku to sales velocity.  Only skus with a positive velocity are
        eligible for reordering.

    Returns
    -------
    list[dict]
        Sorted by sku, each element is {"sku": str, "reorder_quantity": int}.
        Only items that need reordering are included.
    """
    results = []

    for item in items:
        # Skip malformed items (missing required keys or wrong types)
        try:
            sku = item["sku"]
            on_hand = item["on_hand"]
            target = item["target"]
            case_pack = item["case_pack"]
        except (KeyError, TypeError):
            continue

        # Validate types are numeric / string
        if not isinstance(sku, str):
            continue
        try:
            on_hand = int(on_hand)
            target = int(target)
            case_pack = int(case_pack)
        except (TypeError, ValueError):
            continue

        # Skip items with non-positive case_pack
        if case_pack <= 0:
            continue

        # Skip if no positive sales velocity
        velocity = sales_velocity.get(sku, 0)
        try:
            velocity = int(velocity)
        except (TypeError, ValueError):
            continue

        if velocity <= 0:
            continue

        # Determine if reorder is needed
        if on_hand >= target:
            continue

        deficit = target - on_hand

        # Round up deficit to the nearest multiple of case_pack
        reorder_quantity = math.ceil(deficit / case_pack) * case_pack

        results.append({"sku": sku, "reorder_quantity": reorder_quantity})

    # Sort by sku
    results.sort(key=lambda x: x["sku"])

    return results
