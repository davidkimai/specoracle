"""
inventory_reorder module

Provides reorder_plan to compute reorder quantities for inventory items.
"""

import math


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Compute a reorder plan for inventory items.

    Args:
        items: List of dicts, each with keys 'sku', 'on_hand', 'target', 'case_pack'.
        sales_velocity: Mapping of sku to sales velocity (units per period).

    Returns:
        Sorted list of dicts with 'sku' and 'reorder_quantity' for items
        that need reordering.
    """
    results = []

    for item in items:
        # Validate item is a dict with required keys
        if not isinstance(item, dict):
            continue

        required_keys = ("sku", "on_hand", "target", "case_pack")
        if not all(k in item for k in required_keys):
            continue

        sku = item["sku"]
        on_hand = item["on_hand"]
        target = item["target"]
        case_pack = item["case_pack"]

        # Validate types are numeric
        try:
            on_hand = int(on_hand) if isinstance(on_hand, bool) is False else None
            target = int(target) if isinstance(target, bool) is False else None
            case_pack = int(case_pack) if isinstance(case_pack, bool) is False else None
        except (TypeError, ValueError):
            continue

        if on_hand is None or target is None or case_pack is None:
            continue

        # Skip non-positive case_pack
        if case_pack <= 0:
            continue

        # Validate sku is a string
        if not isinstance(sku, str):
            continue

        # Check sales velocity
        velocity = sales_velocity.get(sku, 0)
        try:
            velocity = int(velocity)
        except (TypeError, ValueError):
            continue

        if velocity <= 0:
            continue

        # Compute deficit
        if on_hand >= target:
            continue

        deficit = target - on_hand

        # Round up to nearest multiple of case_pack
        reorder_quantity = math.ceil(deficit / case_pack) * case_pack

        results.append({"sku": sku, "reorder_quantity": reorder_quantity})

    # Sort by sku
    results.sort(key=lambda x: x["sku"])

    return results
