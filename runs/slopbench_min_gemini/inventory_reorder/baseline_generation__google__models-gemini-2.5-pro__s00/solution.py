"""
A module for calculating inventory reorder plans.
"""

from typing import Any, Dict, List

def reorder_plan(
    items: List[Dict[str, Any]],
    sales_velocity: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Calculates a reorder plan for inventory items.

    For each item, if its on-hand quantity is below the target level and its
    sales velocity is positive, this function computes the required reorder
    quantity. The reorder quantity is the deficit rounded up to the nearest
    multiple of the item's case pack size.

    Args:
        items: A list of dictionaries, where each dictionary represents an
               inventory item. Each item must have 'sku' (str), 'on_hand' (int),
               'target' (int), and 'case_pack' (int) keys.
        sales_velocity: A dictionary mapping SKU strings to their integer
                        sales velocity.

    Returns:
        A list of dictionaries, each containing a 'sku' and a 'reorder_quantity'.
        The list is sorted alphabetically by SKU. Items that do not require
        reordering, are malformed, have a non-positive case_pack, or have
        a non-positive sales velocity are excluded.
    """
    reorder_list = []

    for item in items:
        # Validate item structure and required keys
        if not isinstance(item, dict):
            continue

        sku = item.get("sku")
        on_hand = item.get("on_hand")
        target = item.get("target")
        case_pack = item.get("case_pack")

        # Validate types of required keys
        if not (
            isinstance(sku, str) and
            isinstance(on_hand, int) and
            isinstance(target, int) and
            isinstance(case_pack, int)
        ):
            continue

        # Skip items with non-positive case_pack
        if case_pack <= 0:
            continue

        # Skip items with non-positive or absent sales velocity
        velocity = sales_velocity.get(sku, 0)
        if velocity <= 0:
            continue

        # Determine if a reorder is needed
        if on_hand < target:
            deficit = target - on_hand

            # Calculate reorder quantity, rounding up to the nearest case_pack
            # using integer arithmetic to avoid floating point inaccuracies.
            # Formula: ((n + m - 1) // m) * m
            num_cases = (deficit + case_pack - 1) // case_pack
            reorder_quantity = num_cases * case_pack

            reorder_list.append({
                "sku": sku,
                "reorder_quantity": reorder_quantity
            })

    # Sort the results by SKU
    reorder_list.sort(key=lambda x: x["sku"])

    return reorder_list
