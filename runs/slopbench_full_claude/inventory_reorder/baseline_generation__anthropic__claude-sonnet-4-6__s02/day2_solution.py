"""
inventory_reorder module

Provides reorder_plan to compute reorder quantities for inventory items.
"""

import math


def reorder_plan(
    items: list[dict],
    sales_velocity: dict[str, int],
    include_days_of_cover: bool = False,
) -> list[dict]:
    """
    Compute a reorder plan for inventory items.

    Parameters
    ----------
    items : list[dict]
        Each item should contain: sku (str), on_hand (int/float),
        target (int/float), case_pack (int/float).
    sales_velocity : dict[str, int]
        Maps sku to sales velocity. Only skus with velocity > 0 are considered.
    include_days_of_cover : bool, optional
        When True, include days_of_cover_before_reorder (on_hand // velocity)
        in each returned row. Defaults to False.

    Returns
    -------
    list[dict]
        Sorted by sku, each entry has {"sku": str, "reorder_quantity": int}.
        If include_days_of_cover is True, also includes
        {"days_of_cover_before_reorder": int}.
        Only items that need reordering (on_hand < target and velocity > 0) are included.
    """
    results = []

    for item in items:
        # Validate item is a dict with required keys
        if not isinstance(item, dict):
            continue

        required_keys = {"sku", "on_hand", "target", "case_pack"}
        if not required_keys.issubset(item.keys()):
            continue

        sku = item["sku"]
        on_hand = item["on_hand"]
        target = item["target"]
        case_pack = item["case_pack"]

        # Validate types are numeric
        try:
            sku = str(sku)
            on_hand = float(on_hand)
            target = float(target)
            case_pack = float(case_pack)
        except (TypeError, ValueError):
            continue

        # Skip items with non-positive case_pack
        if case_pack <= 0:
            continue

        # Skip if sales_velocity for this sku is <= 0 or absent
        velocity = sales_velocity.get(sku)
        if velocity is None or velocity <= 0:
            continue

        # Only reorder if on_hand is below target
        if on_hand >= target:
            continue

        deficit = target - on_hand

        # Round up deficit to nearest multiple of case_pack
        reorder_quantity = int(math.ceil(deficit / case_pack) * case_pack)

        row = {"sku": sku, "reorder_quantity": reorder_quantity}

        if include_days_of_cover:
            row["days_of_cover_before_reorder"] = int(on_hand // velocity)

        results.append(row)

    # Sort by sku
    results.sort(key=lambda x: x["sku"])

    return results
