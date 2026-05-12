"""
Generates a reorder plan for inventory items based on stock levels and sales.
"""

from typing import Dict, List


def _calculate_reorder_quantity(deficit: int, case_pack: int) -> int:
    """
    Calculates the reorder quantity by rounding the deficit up to the nearest
    multiple of the case pack size.

    Args:
        deficit: The amount by which on_hand is below target. Must be positive.
        case_pack: The size of a reorderable case. Must be positive.

    Returns:
        The computed reorder quantity.
    """
    # This integer arithmetic is equivalent to math.ceil(deficit / case_pack) * case_pack
    # but avoids floating-point inaccuracies.
    return (deficit + case_pack - 1) // case_pack * case_pack


def reorder_plan(
    items: List[Dict], sales_velocity: Dict[str, int]
) -> List[Dict]:
    """
    Computes a reorder plan for a list of inventory items.

    For each item, this function checks if the on-hand quantity is below the
    target level. If it is, and the item has positive sales velocity, it
    calculates the quantity to reorder, rounding up to the nearest case pack.

    Items are skipped if they are malformed, have a non-positive case_pack,
    or have zero or negative sales velocity.

    Args:
        items: A list of inventory items. Each item is a dictionary with keys:
               "sku" (str), "on_hand" (int), "target" (int), "case_pack" (int).
        sales_velocity: A dictionary mapping SKUs to their integer sales
                        velocity.

    Returns:
        A list of dictionaries, each specifying a "sku" and the calculated
        "reorder_quantity". The list is sorted by SKU.

    Raises:
        TypeError: If `items` is not a list or `sales_velocity` is not a dict.
    """
    if not isinstance(items, list):
        raise TypeError("items must be a list of dictionaries.")
    if not isinstance(sales_velocity, dict):
        raise TypeError("sales_velocity must be a dictionary.")

    reorders_to_make = []

    for item in items:
        # Guard against non-dictionary elements in the list.
        if not isinstance(item, dict):
            continue

        # Extract and validate item structure and types.
        sku = item.get("sku")
        on_hand = item.get("on_hand")
        target = item.get("target")
        case_pack = item.get("case_pack")

        is_well_formed = (
            isinstance(sku, str)
            and isinstance(on_hand, int)
            and isinstance(target, int)
            and isinstance(case_pack, int)
        )

        if not is_well_formed:
            continue

        # Apply filtering rules based on business logic.
        item_sales_velocity = sales_velocity.get(sku, 0)
        if case_pack <= 0 or item_sales_velocity <= 0:
            continue

        # Determine if a reorder is needed.
        deficit = target - on_hand
        if deficit > 0:
            quantity_to_order = _calculate_reorder_quantity(deficit, case_pack)
            reorders_to_make.append({
                "sku": sku,
                "reorder_quantity": quantity_to_order
            })

    # Return the final plan, sorted by SKU for deterministic output.
    return sorted(reorders_to_make, key=lambda r: r["sku"])
