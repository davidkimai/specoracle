"""
A module for indexing user purchase events from a list of event dictionaries.
"""

def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    This function processes a list of event dictionaries and aggregates purchase
    data for each user. It filters for events that are valid purchases, which
    are defined as having:
    - A "kind" field with the value "purchase".
    - A "user_id" field with a non-empty string value.
    - An "amount" field with an integer value.

    Events that do not meet these criteria are ignored. The input list and its
    contained dictionaries are not mutated.

    Args:
        events: A list of dictionaries, where each dictionary represents an event.

    Returns:
        A dictionary where keys are user_ids and values are dictionaries
        containing the total purchase count and the sum of purchase amounts
        for that user. The format is:
        {
            "user_id_1": {"count": N, "total": T},
            "user_id_2": {"count": M, "total": S},
            ...
        }
        Returns an empty dictionary if no valid purchase events are found.
    """
    user_index: dict[str, dict[str, int]] = {}

    for event in events:
        # Safely access event data using .get() to avoid KeyErrors if
        # a key is missing. The default of None will fail the checks below.
        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        # --- Validation checks for a valid purchase event ---

        # 1. The event kind must be "purchase".
        if kind != "purchase":
            continue

        # 2. The user_id must be a non-empty string.
        #    isinstance() handles non-string types, `not user_id` handles "".
        if not isinstance(user_id, str) or not user_id:
            continue

        # 3. The amount must be an integer.
        if not isinstance(amount, int):
            continue

        # --- Aggregation logic ---

        # If the user is not yet in the index, initialize their record.
        if user_id not in user_index:
            user_index[user_id] = {"count": 0, "total": 0}

        # Update the count and total amount for the user.
        user_index[user_id]["count"] += 1
        user_index[user_id]["total"] += amount

    return user_index
