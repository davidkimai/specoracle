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
        Each element should contain the keys: sku, on_hand, target, case_pack.
    sales_velocity : dict[str, int]
        Maps sku to its sales velocity.  Only skus with a positive velocity
        are candidates for reordering.
    include_days_of_cover : bool, optional
        When True, each returned row also contains
        ``days_of_cover_before_reorder`` computed as
        ``on_hand // sales_velocity[sku]``.  Defaults to False.

    Returns
    -------
    list[dict]
        Sorted by sku, each entry has {"sku": str, "reorder_quantity": int}
        and, when *include_days_of_cover* is True, also
        {"days_of_cover_before_reorder": int}.
    """
    results = []

    for item in items:
        # --- validate item structure ---
        if not isinstance(item, dict):
            continue

        # Required keys must be present
        if not all(k in item for k in ("sku", "on_hand", "target", "case_pack")):
            continue

        sku = item["sku"]
        on_hand = item["on_hand"]
        target = item["target"]
        case_pack = item["case_pack"]

        # sku must be a string
        if not isinstance(sku, str):
            continue

        # Numeric fields must be numeric (int or float, not bool)
        for val in (on_hand, target, case_pack):
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                break
        else:
            # case_pack must be positive
            if case_pack <= 0:
                continue

            # Check sales velocity
            velocity = sales_velocity.get(sku)
            if velocity is None or velocity <= 0:
                continue

            # Only reorder when on_hand is below target
            deficit = target - on_hand
            if deficit <= 0:
                continue

            # Round up deficit to nearest multiple of case_pack
            reorder_quantity = math.ceil(deficit / case_pack) * case_pack

            row = {"sku": sku, "reorder_quantity": int(reorder_quantity)}

            if include_days_of_cover:
                row["days_of_cover_before_reorder"] = int(on_hand) // int(velocity)

            results.append(row)
            continue

        # The for-else did not reach 'else' (a bad value was found)
        continue

    results.sort(key=lambda x: x["sku"])
    return results
