"""
This module provides functionality to calculate inventory reorder plans.
"""

from typing import List, Dict, Any

def reorder_plan(
    items: List[Dict[str, Any]],
    sales_velocity: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Calculates the reorder quantities for inventory items based on stock levels,
    targets, and sales velocity.

    The function processes a list of items, filtering for those that require
    reordering. An item needs reordering if its on-hand quantity is below its
    target level and it has a positive sales velocity. Malformed items, items
    with non-positive case packs, or items with zero or negative sales velocity
    are ignored.

    The reorder quantity is calculated to cover the deficit (target - on_hand)
    and is rounded up to the nearest whole case pack.

    Args:
        items: A list of item dictionaries. Each dictionary should contain:
            - 'sku' (str): The stock keeping unit.
            - 'on_hand' (int): The current number of units in stock.
            - 'target' (int): The desired number of units to have in stock.
            - 'case_pack' (int): The number of units in a single orderable case.
        sales_velocity: A dictionary mapping SKUs to their sales velocity. Items
            with no entry or a non-positive velocity will not be reordered.

    Returns:
        A list of dictionaries for items that need reordering. Each dictionary
        contains:
            - 'sku' (str): The item's SKU.
            - 'reorder_quantity' (int): The calculated quantity to reorder.
        The list is sorted alphabetically by SKU.
    """
    reorder_list = []

    for item in items:
        # 1. Validate item structure and types
        if not isinstance(item, dict):
            continue

        sku = item.get('sku')
        on_hand = item.get('on_hand')
        target = item.get('target')
        case_pack = item.get('case_pack')

        if not (isinstance(sku, str) and
                isinstance(on_hand, int) and
                isinstance(target, int) and
                isinstance(case_pack, int)):
            # Skip malformed items (e.g., missing keys, wrong value types)
            continue

        # 2. Validate business rule constraints for the item
        if case_pack <= 0:
            continue

        # 3. Check for valid sales velocity
        velocity = sales_velocity.get(sku)
        if not isinstance(velocity, int) or velocity <= 0:
            continue

        # 4. Determine if a reorder is needed
        if on_hand < target:
            deficit = target - on_hand

            # 5. Calculate reorder quantity, rounding up to the nearest multiple
            #    of case_pack. The formula `(a + b - 1) // b` computes the
            #    ceiling of `a / b` using integer arithmetic for positive `a`, `b`.
            num_cases = (deficit + case_pack - 1) // case_pack
            reorder_quantity = num_cases * case_pack

            reorder_list.append({
                "sku": sku,
                "reorder_quantity": reorder_quantity,
            })

    # 6. Sort the final list by SKU before returning
    return sorted(reorder_list, key=lambda r: r['sku'])
