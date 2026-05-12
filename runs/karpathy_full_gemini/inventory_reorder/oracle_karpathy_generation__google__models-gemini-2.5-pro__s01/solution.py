"""
A module for calculating inventory reorder plans.
"""

from typing import Any


def reorder_plan(
    items: list[dict[str, Any]],
    sales_velocity: dict[str, int]
) -> list[dict[str, Any]]:
    """
    Calculates a reorder plan based on current inventory, targets, and sales.

    This function processes a list of inventory items to determine which ones
    need reordering. An item is considered for reorder if its on-hand quantity
    is below its target level and it has a positive sales velocity.

    The reorder quantity is calculated to cover the deficit (target - on_hand),
    rounded up to the nearest case pack size.

    Args:
        items: A list of dictionaries, where each dictionary represents an
               inventory item. Each item must have 'sku', 'on_hand', 'target',
               and 'case_pack' keys. Items that are malformed (e.g., missing
               keys, non-numeric values for quantities, non-positive case_pack)
               are skipped.
        sales_velocity: A dictionary mapping item SKUs to their integer sales
                        velocity. Items with no entry or a non-positive sales
                        velocity will not be reordered.

    Returns:
        A list of dictionaries for items that need to be reordered. Each
        dictionary contains the 'sku' and the calculated 'reorder_quantity'.
        The list is sorted alphabetically by SKU.
    """
    reorder_list = []

    for item in items:
        try:
            # Ensure required keys exist and values are of the correct type.
            sku = str(item["sku"])
            on_hand = int(item["on_hand"])
            target = int(item["target"])
            case_pack = int(item["case_pack"])
        except (KeyError, ValueError, TypeError):
            # Skip items with missing keys or values that cannot be parsed.
            continue

        # Skip items with a non-positive case pack size.
        if case_pack <= 0:
            continue

        # Do not reorder if sales velocity is zero, negative, or absent.
        if sales_velocity.get(sku, 0) <= 0:
            continue

        # Reorder only when current stock is below the target level.
        if on_hand < target:
            deficit = target - on_hand

            # Round up the deficit to the nearest multiple of case_pack.
            # This integer arithmetic is equivalent to math.ceil(deficit / case_pack).
            num_cases = (deficit + case_pack - 1) // case_pack
            reorder_quantity = num_cases * case_pack

            reorder_list.append({
                "sku": sku,
                "reorder_quantity": reorder_quantity
            })

    # Return the final list sorted by SKU.
    reorder_list.sort(key=lambda x: x["sku"])

    return reorder_list
