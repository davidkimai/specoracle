"""
Module for calculating inventory reorder plans.
"""

from typing import List, Dict, Any


def reorder_plan(
    items: List[Dict[str, Any]],
    sales_velocity: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Calculates a reorder plan for inventory items.

    For each item, if the on-hand quantity is below the target and the item
    has a positive sales velocity, a reorder quantity is calculated. The
    reorder quantity is the deficit rounded up to the nearest multiple of the
    item's case pack size.

    Args:
        items: A list of dictionaries, where each dictionary represents an
               inventory item with 'sku', 'on_hand', 'target', and
               'case_pack' keys.
        sales_velocity: A dictionary mapping SKUs to their sales velocity.
                        Items with no entry or a non-positive velocity will
                        not be reordered.

    Returns:
        A list of dictionaries, each containing a 'sku' and a
        'reorder_quantity', sorted by SKU. Malformed items, items with
        non-positive case_pack, or items with non-positive sales velocity
        are skipped.
    """
    reorders = []
    required_keys = {"sku", "on_hand", "target", "case_pack"}

    for item in items:
        # Validate item structure and types
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            continue

        sku = item.get("sku")
        on_hand = item.get("on_hand")
        target = item.get("target")
        case_pack = item.get("case_pack")

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

        # Skip if sales_velocity is <= 0 or absent
        if sales_velocity.get(sku, 0) <= 0:
            continue

        # Compute reorder quantity if on_hand is below target
        if on_hand < target:
            deficit = target - on_hand

            # Calculate how many cases are needed by rounding up the division.
            # Using integer arithmetic for ceiling division is robust.
            num_cases_needed = (deficit + case_pack - 1) // case_pack
            reorder_quantity = num_cases_needed * case_pack

            reorders.append({"sku": sku, "reorder_quantity": reorder_quantity})

    # Sort the result by SKU
    reorders.sort(key=lambda r: r["sku"])

    return reorders
