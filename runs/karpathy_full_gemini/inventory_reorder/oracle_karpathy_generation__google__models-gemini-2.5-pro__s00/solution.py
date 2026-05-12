"""
A module for calculating inventory reorder plans.
"""

def reorder_plan(items: list[dict], sales_velocity: dict[str, int]) -> list[dict]:
    """
    Generates a reorder plan based on current inventory, targets, and sales velocity.

    For each item, if the on-hand quantity is below the target and sales
    velocity is positive, a reorder quantity is calculated. The reorder
    quantity is the deficit rounded up to the nearest case pack size.

    Args:
        items: A list of item dictionaries. Each dictionary is expected to contain:
            'sku' (str): The stock keeping unit.
            'on_hand' (int): The current quantity in stock.
            'target' (int): The desired quantity in stock.
            'case_pack' (int): The number of items in a case.
        sales_velocity: A dictionary mapping SKU to sales per period.

    Returns:
        A list of dictionaries for items that need reordering, sorted by SKU.
        Each dictionary contains:
            'sku' (str): The item's SKU.
            'reorder_quantity' (int): The calculated quantity to reorder.

    Items are skipped if they are malformed (e.g., missing keys, wrong data types),
    have a non-positive case_pack, or have a non-positive or missing sales
    velocity.
    """
    plan = []

    for item in items:
        try:
            sku = item['sku']
            on_hand = item['on_hand']
            target = item['target']
            case_pack = item['case_pack']

            # Validate data types for robustness.
            if not isinstance(sku, str) or \
               not isinstance(on_hand, int) or \
               not isinstance(target, int) or \
               not isinstance(case_pack, int):
                continue

            # Skip items with a non-positive case pack.
            if case_pack <= 0:
                continue

            # Skip items with zero or negative sales velocity, or if the SKU is not found.
            if sales_velocity.get(sku, 0) <= 0:
                continue

            # Determine if a reorder is needed.
            if on_hand < target:
                deficit = target - on_hand

                # Calculate reorder quantity, rounding up to the nearest multiple of case_pack.
                # This uses integer arithmetic to avoid floating point inaccuracies.
                # It's equivalent to math.ceil(deficit / case_pack) * case_pack.
                num_cases = (deficit + case_pack - 1) // case_pack
                reorder_quantity = num_cases * case_pack

                plan.append({"sku": sku, "reorder_quantity": reorder_quantity})

        except (KeyError, TypeError):
            # Skip
