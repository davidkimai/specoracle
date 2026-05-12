"""
Module for generating inventory reorder plans.
"""

from typing import List, Dict, Any, Optional


def _calculate_reorder_quantity(deficit: int, case_pack: int) -> int:
    """
    Calculates the required order quantity by rounding the deficit up to the
    nearest multiple of the case_pack.

    Args:
        deficit: The amount by which on_hand inventory is below the target.
        case_pack: The number of units in a single orderable case.

    Returns:
        The total number of units to reorder.
    """
    # This integer arithmetic computes ceiling division without using floats.
    # It assumes case_pack is positive, which is validated by the caller.
    num_cases = (deficit + case_pack - 1) // case_pack
    return num_cases * case_pack


def _evaluate_item_for_reorder(
    item: Any, sales_velocity: Dict[str, int]
) -> Optional[Dict[str, Any]]:
    """
    Processes a single item to determine if a reorder is needed.

    This function validates the item's structure, type, and business rules.
    If all conditions for a reorder are met, it computes the reorder quantity
    and returns a reorder instruction dictionary. Otherwise, it returns None.

    Args:
        item: A dictionary representing an inventory item.
        sales_velocity: A dictionary mapping SKUs to their sales rates.

    Returns:
        A dictionary with "sku" and "reorder_quantity" if a reorder is
        needed, otherwise None.
    """
    if not isinstance(item, dict):
        return None

    sku = item.get("sku")
    on_hand = item.get("on_hand")
    target = item.get("target")
    case_pack = item.get("case_pack")

    # A single, flat guard clause for all validation steps.
    # This checks for presence, correct types, and valid business rules.
    if not all(
        [
            isinstance(sku, str),
            isinstance(on_hand, int),
            isinstance(target, int),
            isinstance(case_pack, int),
            case_pack > 0,
            sales_velocity.get(sku, 0) > 0,
            on_hand < target,
        ]
    ):
        return None

    deficit = target - on_hand
    reorder_quantity = _calculate_reorder_quantity(deficit, case_pack)

    return {"sku": sku, "reorder_quantity": reorder_quantity}


def reorder_plan(
    items: List[Dict[str, Any]], sales_velocity: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Generates a sorted reorder plan for inventory items.

    For each item, this function checks if the on-hand quantity is below the
    target level. If it is, and the item has positive sales velocity, it
    calculates the number of units to reorder, rounding up to the nearest
    full case pack.

    Items that are malformed, have a non-positive case_pack, or lack positive
    sales velocity are skipped.

    Args:
        items: A list of dictionaries, where each dictionary represents an
               inventory item with keys 'sku', 'on_hand', 'target', and
               'case_pack'.
        sales_velocity: A dictionary mapping item SKUs to their integer sales
                        velocity.

    Returns:
        A list of reorder instruction dictionaries, sorted alphabetically by
        SKU. Each dictionary contains 'sku' and 'reorder_quantity'.

    Raises:
        TypeError: If 'items' is not a list or 'sales_velocity' is not a dict.
    """
    if not isinstance(items, list):
        raise TypeError("Input 'items' must be a list.")
    if not isinstance(sales_velocity, dict):
        raise TypeError("Input 'sales_velocity' must be a dict.")

    reorders = []
    for item in items:
        reorder_instruction = _evaluate_item_for_reorder(item, sales_velocity)
        if reorder_instruction:
            reorders.append(reorder_instruction)

    return sorted(reorders, key=lambda r: r["sku"])
