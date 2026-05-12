"""
Module for generating inventory reorder plans based on sales and stock levels.
"""

import math
from typing import Any, Dict, List


def _is_valid_item_structure(item: Any) -> bool:
    """
    Checks if an item has the required keys and correct data types.

    Args:
        item: The item to validate.

    Returns:
        True if the item is a dictionary with the correct structure and types,
        False otherwise.
    """
    if not isinstance(item, dict):
        return False

    required_fields = {
        "sku": str,
        "on_hand": int,
        "target": int,
        "case_pack": int,
    }

    for key, expected_type in required_fields.items():
        if key not in item:
            return False
        if not isinstance(item[key], expected_type):
            return False

    return True


def _calculate_reorder_quantity(deficit: int, case_pack: int) -> int:
    """
    Computes reorder quantity by rounding a deficit up to the nearest multiple.

    Args:
        deficit: The number of units needed to reach the target. Must be > 0.
        case_pack: The number of units in a case. Must be > 0.

    Returns:
        The calculated reorder quantity, a multiple of case_pack.
    """
    num_cases = math.ceil(deficit / case_pack)
    return num_cases * case_pack


def reorder_plan(
    items: List[Dict[str, Any]],
    sales_velocity: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Generates a reorder plan based on inventory levels, targets, and sales.

    For each item, if its on-hand quantity is below its target and it has
    positive sales velocity, a reorder quantity is calculated. The quantity
    is the deficit rounded up to the nearest multiple of the item's case pack.

    Malformed items or items with non-positive case packs are skipped.

    Args:
        items: A list of dictionaries, each representing an inventory item.
               Expected keys: 'sku' (str), 'on_hand' (int), 'target' (int),
               'case_pack' (int).
        sales_velocity: A dictionary mapping SKUs to their integer sales
                        velocity. Items with no entry or non-positive velocity
                        will not be reordered.

    Returns:
        A list of dictionaries for items that need reordering, sorted
        alphabetically by SKU. Each dictionary contains 'sku' and
        'reorder_quantity'.
    """
    reorder_list = []

    for item in items:
        if not _is_valid_item_structure(item):
            continue

        # At this point, keys are guaranteed to exist with correct types.
        sku = item["sku"]
        on_hand = item["on_hand"]
        target = item["target"]
        case_pack = item["case_pack"]

        # A non-positive case_pack makes reordering logic invalid.
        if case_pack <= 0:
            continue

        # Do not reorder items that are not selling.
        if sales_velocity.get(sku, 0) <= 0:
            continue

        # Reorder is only needed if inventory is below the target.
        if on_hand >= target:
            continue

        deficit = target - on_hand
        quantity_to_order = _calculate_reorder_quantity(deficit, case_pack)

        reorder_list.append({
            "sku": sku,
            "reorder_quantity": quantity_to_order
        })

    reorder_list.sort(key=lambda r: r["sku"])

    return reorder_list
