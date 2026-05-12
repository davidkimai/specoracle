import math


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Compute a reorder plan for inventory items.

    Parameters
    ----------
    items : list[dict]
        Each element should contain keys: sku, on_hand, target, case_pack.
    sales_velocity : dict[str, int]
        Maps sku to sales velocity (units per period).

    Returns
    -------
    list[dict]
        Sorted by sku, each entry has {"sku": str, "reorder_quantity": int}.
        Only items that need reordering (on_hand < target and positive velocity)
        are included.
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

        # Validate that sku is a string
        if not isinstance(sku, str):
            continue

        # Validate numeric fields are actually numeric (int or float, not bool)
        for val in (on_hand, target, case_pack):
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                break
        else:
            # All numeric checks passed; proceed
            # Skip non-positive case_pack
            if case_pack <= 0:
                continue

            # Skip if sales velocity is absent or non-positive
            velocity = sales_velocity.get(sku)
            if velocity is None or velocity <= 0:
                continue

            # Only reorder when on_hand is strictly below target
            if on_hand < target:
                deficit = target - on_hand
                # Round up deficit to nearest multiple of case_pack
                reorder_quantity = math.ceil(deficit / case_pack) * case_pack
                results.append({"sku": sku, "reorder_quantity": int(reorder_quantity)})
            continue

        # If we broke out of the for loop, a numeric field was invalid
        continue

    # Sort by sku
    results.sort(key=lambda x: x["sku"])
    return results
