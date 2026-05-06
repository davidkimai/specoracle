import math


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Compute a reorder plan for inventory items.

    Args:
        items: List of dicts with keys 'sku', 'on_hand', 'target', 'case_pack'.
        sales_velocity: Mapping of sku to sales velocity (units per period).

    Returns:
        Sorted list of dicts with 'sku' and 'reorder_quantity' for items
        that need reordering.
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

        # Validate that sku is a string and numeric fields are numbers
        if not isinstance(sku, str):
            continue
        if not isinstance(on_hand, (int, float)) or isinstance(on_hand, bool):
            continue
        if not isinstance(target, (int, float)) or isinstance(target, bool):
            continue
        if not isinstance(case_pack, (int, float)) or isinstance(case_pack, bool):
            continue

        # Skip items with non-positive case_pack
        if case_pack <= 0:
            continue

        # Skip if sales_velocity for this sku is <= 0 or absent
        velocity = sales_velocity.get(sku)
        if velocity is None or velocity <= 0:
            continue

        # Compute deficit
        deficit = target - on_hand
        if deficit <= 0:
            continue

        # Round up to nearest multiple of case_pack
        reorder_quantity = math.ceil(deficit / case_pack) * int(case_pack)

        results.append({"sku": sku, "reorder_quantity": reorder_quantity})

    # Sort by sku
    results.sort(key=lambda x: x["sku"])

    return results
