"""
A module for indexing user purchase events from a list of event data.
"""

from typing import Any


def build_user_purchase_index(
    events: list[dict[str, Any]]
) -> dict[str, dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    This function processes a list of event dictionaries, filtering for valid
    "purchase" events. A valid purchase event must have a "kind" of "purchase",
    a non-empty string "user_id", and an integer "amount".

    The function aggregates the number of purchases and the total amount spent
    for each user across all valid events.

    Args:
        events: A list of event dictionaries. Each dictionary may contain
                'user_id', 'kind', and 'amount' keys.

    Returns:
        A dictionary where keys are user_ids from valid purchase events.
        Each value is a dictionary containing the total purchase 'count' and
        the summed 'total' amount for that user.
        Example: {'user1': {'count': 2, 'total': 150}}
    """
    user_index: dict[str, dict[str, int]] = {}

    for event in events:
        # Use .get() for safe access to potentially missing keys.
        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        # An event is included only if it meets all specified criteria:
        # - The 'kind' must be exactly "purchase".
        # - The 'user_id' must be a non-empty string.
        # - The 'amount' must be an integer.
        if (
            kind == "purchase"
            and isinstance(user_id, str)
            and user_id
            and isinstance(amount, int)
        ):
            # If the user is not yet in the index, initialize their entry.
            if user_id not in user_index:
                user_index[user_id] = {"count": 0, "total": 0}

            # Update the user's purchase count and total amount.
            user_index[user_id]["count"] += 1
            user_index[user_id]["total"] += amount

    return user_index
