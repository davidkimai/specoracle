"""
inventory_reorder module
Provides reorder_plan function to compute inventory reorder quantities.
"""

import math


def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Compute a reorder plan for inventory items.

    Args:
        items: List of dicts with keys 'sku', 'on_hand', 'target', 'case_pack'.
        sales_velocity: Dict mapping sku to sales velocity (units per period).

    Returns:
        Sorted list of dicts with 'sku' and 'reorder_quantity' for items
        that need reordering.
    """
    results = []

    for item in items:
        # Validate item is a dict with required keys
        if not isinstance(item, dict):
            continue

        required_keys = ('sku', 'on_hand', 'target', 'case_pack')
        if not all(k in item for k in required_keys):
            continue

        sku = item['sku']
        on_hand = item['on_hand']
        target = item['target']
        case_pack = item['case_pack']

        # Validate types are numeric (int or float) and sku is a string
        if not isinstance(sku, str):
            continue

        try:
            on_hand = int(on_hand)
            target = int(target)
            case_pack = int(case_pack)
        except (TypeError, ValueError):
            continue

        # Skip items with non-positive case_pack
        if case_pack <= 0:
            continue

        # Check sales velocity: skip if <= 0 or absent
        velocity = sales_velocity.get(sku)
        if velocity is None or velocity <= 0:
            continue

        # Compute deficit
        deficit = target - on_hand
        if deficit <= 0:
            continue

        # Round up to nearest multiple of case_pack
        reorder_quantity = math.ceil(deficit / case_pack) * case_pack

        results.append({'sku': sku, 'reorder_quantity': reorder_quantity})

    # Sort by sku
    results.sort(key=lambda x: x['sku'])

    return results
