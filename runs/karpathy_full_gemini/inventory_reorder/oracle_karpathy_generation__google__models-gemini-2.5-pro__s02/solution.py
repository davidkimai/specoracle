"""
Module for calculating inventory reorder plans.
"""

from typing import List, Dict, Any

def reorder_plan(
    items: List[Dict[str, Any]],
    sales_velocity: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Generates a reorder plan for inventory items based on stock levels and sales.

    This function processes a list of inventory items, determines if a reorder is
    necessary based on the on-hand quantity versus the target quantity, and
    calculates the reorder amount. The reorder quantity is always rounded up to
    the nearest case pack size.

    Items are considered for reorder only if they have a positive sales velocity.
    Malformed items (e.g., missing keys, wrong data types), items with a
    non-positive case_pack, or items with zero or negative sales velocity are
    skipped.

    Args:
        items: A list of dictionaries, where each dictionary represents an item.
               Expected keys are 'sku' (str), 'on_hand' (int), 'target' (int),
               and 'case_pack' (int).
        sales_velocity: A dictionary mapping item SKUs to their integer sales
                        velocity. Items not in this dictionary or with a
                        velocity of 0 or less will not be reordered.

    Returns:
        A list of dictionaries for items that need to be reordered. Each
        dictionary contains the 'sku' and the calculated 'reorder_quantity'.
        The list is sorted alphabetically by SKU.
    """
    reorder_list = []

    for item in items:
        # A try-except block is a robust way to handle malformed `item`
        # dictionaries (e.g., missing keys, values of incorrect types).
        try:
            sku = item['sku']
            on_hand = item['on_hand']
            target = item['target']
            case_pack = item['case_pack']

            # Skip items with non-positive case_pack. This also implicitly
            # handles non-numeric types for case_pack, which would raise a
            # TypeError caught below.
            if not isinstance(case_pack, int) or case_pack <= 0:
                continue

            # Do not reorder if sales_velocity is <= 0 or absent.
            # The .get() method with a default of 0 handles the absent case.
            if sales_velocity.get(sku, 0) <= 0:
                continue

            # Reorder only when on-hand stock is below the target level.
            if on_hand < target:
                deficit = target - on_hand

                # Round up the deficit to the nearest multiple of case_pack.
                # Integer arithmetic `(a + b - 1) // b` is equivalent to
                # `ceil(a / b)`, avoiding floating-point math.
                num_cases = (deficit + case_pack - 1) // case_pack
                reorder_quantity = num_cases * case_pack

                reorder_list.append({
                    "sku": sku,
                    "reorder_quantity": reorder_quantity,
                })

        except (KeyError, TypeError):
            # Skip malformed items: KeyError for missing keys, TypeError for
            # operations on incompatible types (e.g., 'target' - 'on_hand'
            # if one is not a number).
            continue

    # Return the final list, sorted by SKU.
    reorder_list.sort(key=lambda x: x['sku'])

    return reorder_list
