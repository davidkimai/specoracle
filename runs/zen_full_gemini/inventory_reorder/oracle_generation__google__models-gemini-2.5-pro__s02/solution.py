import math
from typing import Dict, List, Any

#
# Helper functions to promote clarity and single-responsibility.
#

def _is_item_well_formed(item: Dict[str, Any]) -> bool:
    """
    Checks if an item dictionary has the required structure and types.

    Args:
        item: A dictionary potentially representing an inventory item.

    Returns:
        True if the item is well-formed, False otherwise.
    """
    if not isinstance(item, dict):
        return False

    required_keys = {
        "sku": str,
        "on_hand": int,
        "target": int,
        "case_pack": int,
    }

    for key, expected_type in required_keys.items():
        if key not in item or not isinstance(item.get(key), expected_type):
            return False

    return True


def _calculate_reorder_quantity(deficit: int, case_pack: int) -> int:
    """
    Computes the quantity to order, rounded up to the nearest case pack.

    This function assumes valid, positive inputs as per the calling context's
    guard clauses.

    Args:
        deficit: The number of units needed to reach the target.
        case_pack: The number of units in a single orderable case.

    Returns:
        The total number of units to reorder.
    """
    # math.ceil returns a float, so we must cast to int.
    num_cases_needed = math.ceil(deficit / case_pack)
    return int(num_cases_needed * case_pack)


#
# Public entry point.
#

def reorder_plan(
    items: List[Dict[str, Any]], sales_velocity: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Generates a reorder plan for inventory items based on stock levels.

    Args:
        items: A list of dictionaries, where each dictionary represents an
               inventory item with keys 'sku', 'on_hand', 'target', and
               'case_pack'. Malformed items are skipped.
        sales_velocity: A dictionary mapping SKUs to their integer sales
                        velocity. Items with no entry or a non-positive
                        velocity will not be reordered.

    Returns:
        A list of dictionaries, each with 'sku' and 'reorder_quantity',
        sorted alphabetically by SKU.
    """
    reorders_to_make = []

    for item in items:
        if not _is_item_well_formed(item):
            continue

        sku = item["sku"]
        on_hand = item["on_hand"]
        target = item["target"]
        case_pack = item["case_pack"]

        # A non-positive case_pack makes reordering impossible.
        if case_pack <= 0:
            continue

        # A non-positive sales velocity indicates no demand.
        velocity = sales_velocity.get(sku)
        if not isinstance(velocity, int) or velocity <= 0:
            continue

        # Reorder is only necessary if stock is below the target level.
        if on_hand < target:
            deficit = target - on_hand
            reorder_quantity = _calculate_reorder_quantity(deficit, case_pack)
            reorders_to_make.append({
                "sku": sku,
                "reorder_quantity": reorder_quantity,
            })

    # The final plan must be sorted for consistent output.
    return sorted(reorders_to_make, key=lambda r: r["sku"])
