"""
This module provides functionality to generate an inventory reorder plan.
"""

from typing import Any

def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Generates a reorder plan based on current inventory, targets, and sales.

    For each item, if its on-hand quantity is below the target and it has
    a positive sales velocity, a reorder quantity is calculated. The reorder
    quantity is the deficit rounded up to the nearest whole case pack.

    Malformed items, items with a non-positive case_pack, or items with
    a non-positive or absent sales velocity are skipped.

    Args:
        items: A list of item dictionaries. Each dictionary must contain:
               - 'sku' (str): The stock-keeping unit.
               - 'on_hand' (int): The current number of units in stock.
               - 'target' (int): The desired number of units to have in stock.
               - 'case_pack' (int): The number of units in a single case.
        sales_velocity: A dictionary mapping SKUs to their recent sales
                        velocity. Items with no entry or a non-positive
                        velocity will not be reordered.

    Returns:
        A list of dictionaries for items that need to be reordered. Each
        dictionary contains:
        - 'sku' (str): The item's SKU.
        - 'reorder_quantity' (int): The calculated number of units to order.
        The list is sorted alphabetically by SKU.
    """
    reorders: list[dict[str, Any]] = []
    required_keys = {'sku', 'on_hand', 'target', 'case_pack'}

    for item in items:
        # Validate item structure: must be a dict with all required keys
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            continue

        sku = item['sku']
        on_hand = item['on_hand']
        target = item['target']
        case_pack = item['case_pack']

        # Validate item value types
        if not (isinstance(sku, str) and
                isinstance(on_hand, int) and
                isinstance(target, int) and
                isinstance(case_pack, int)):
            continue

        # Skip items with non-positive case_pack
        if case_pack <= 0:
            continue

        # Skip items with zero, negative, or absent sales velocity
        velocity = sales_velocity.get(sku, 0)
        if not isinstance(velocity, int) or velocity <= 0:
            continue

        # Determine if a reorder is needed
        if on_hand < target:
            deficit = target - on_hand

            # Calculate reorder quantity, rounding up to the nearest case_pack
            # The formula (a + b - 1) // b computes ceiling division for integers
            num_cases = (deficit + case_pack - 1) // case_pack
            reorder_quantity = num_cases * case_pack

            reorders.append({
                'sku': sku,
                'reorder_quantity': reorder_quantity
            })

    # Return the reorder plan, sorted by SKU
    reorders.sort(key=lambda x: x['sku'])
    return reorders
