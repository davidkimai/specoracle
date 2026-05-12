"""
A module for calculating inventory reorder plans.
"""

from typing import List, Dict, Any

def reorder_plan(
    items: List[Dict[str, Any]],
    sales_velocity: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Calculates a reorder plan for inventory items.

    For each item, if the on-hand quantity is below the target and the item
    has positive sales velocity, a reorder quantity is calculated. This
    quantity is the deficit rounded up to the nearest case pack multiple.

    Args:
        items: A list of dictionaries, where each dictionary represents an
               inventory item. Expected keys are 'sku' (str), 'on_hand' (int),
               'target' (int), and 'case_pack' (int).
        sales_velocity: A dictionary mapping SKU strings to their integer
                        sales velocity.

    Returns:
        A list of dictionaries, each containing a 'sku' and a 'reorder_quantity',
        sorted alphabetically by SKU. Malformed items, items with non-positive
        case packs, or items with non-positive sales velocity are skipped.
    """
    reorder_list = []

    for item in items:
        # --- Validation Step ---
        # Skip items that are not dictionaries or are missing required keys
        if not isinstance(item, dict):
            continue

        sku = item.get('sku')
        on_hand = item.get('on_hand')
        target = item.get('target')
        case_pack = item.get('case_pack')

        # Skip items with missing or incorrectly typed essential fields
        if not (
            isinstance(sku, str) and
            isinstance(on_hand, int) and
            isinstance(target, int) and
            isinstance(case_pack, int)
        ):
            continue

        # --- Business Rule Filtering ---
        # Skip items with non-positive case_pack
        if case_pack <= 0:
            continue

        # Skip items with no or non-positive sales velocity
        velocity = sales_velocity.get(sku, 0)
        if velocity <= 0:
            continue

        # --- Reorder Calculation ---
        # Determine if a reorder is needed
        if on_hand < target:
            deficit = target - on_hand

            # Calculate the number of cases needed, rounding up to the nearest
            # whole case. The formula `(a + b - 1) // b` is a robust way
            # to perform ceiling division with integers.
            num_cases_to_order = (deficit + case_pack - 1) // case_pack
            reorder_quantity = num_cases_to_order * case_pack

            reorder_list.append({
                "sku": sku,
                "reorder_quantity": reorder_quantity,
            })

    # --- Final Sorting ---
    # Sort the results alphabetically by SKU
    reorder_list.sort(key=lambda plan: plan['sku'])

    return reorder_list
