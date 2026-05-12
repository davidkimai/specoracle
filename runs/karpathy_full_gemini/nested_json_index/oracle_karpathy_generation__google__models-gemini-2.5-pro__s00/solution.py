"""
Module for processing event data to build a user purchase index.
"""

def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    """
    Builds an index of user purchases from a list of event dictionaries.

    This function processes a list of events, filtering for valid purchase
    events and aggregating the total number of purchases and the total amount
    spent by each user.

    Args:
        events: A list of dictionaries, where each dictionary represents an
                event. An event may contain 'user_id', 'kind', and 'amount'.

    Returns:
        A dictionary keyed by user_id. Each value is a dictionary containing:
        - 'count': The total number of valid purchases for the user.
        - 'total': The sum of the 'amount' for all valid purchases.

    An event is considered a valid purchase if it meets all the following
    criteria:
    - The 'kind' key has a value of "purchase".
    - The 'user_id' key has a value that is a non-empty string.
    - The 'amount' key has a value that is an integer.
    
    The input list and its dictionaries are not mutated.
    """
    user_index: dict[str, dict[str, int]] = {}

    for event in events:
        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        is_valid_purchase = (
            kind == "purchase" and
            isinstance(user_id, str) and user_id and
            isinstance(amount, int)
        )

        if is_valid_purchase:
            # At this point, type checkers can infer that user_id is a non-empty
            # string and amount is an integer.
            if user_id not in user_index:
                # First valid purchase for this user. Initialize their record.
                user_index[user_id] = {"count": 1, "total": amount}
            else:
                # This user already has a record. Update it.
                user_index[user_id]["count"] += 1
                user_index[user_id]["total"] += amount

    return user_index
