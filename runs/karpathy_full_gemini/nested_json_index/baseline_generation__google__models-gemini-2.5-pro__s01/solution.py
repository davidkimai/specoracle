"""
A module for securely indexing user purchase events from nested JSON-like data.
"""

from typing import Any

def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    This function processes a list of event dictionaries, filtering for valid
    purchase events. A valid purchase event must have a 'kind' of "purchase",
    a non-empty string 'user_id', and an integer 'amount'.

    The function aggregates the total number of purchases and the total amount
    spent for each user. It does not mutate the input list or any of the
    dictionaries within it.

    Args:
        events: A list of event dictionaries. Each event may contain 'user_id',
                'kind', and 'amount' keys.

    Returns:
        A dictionary where keys are user IDs and values are dictionaries
        containing the 'count' of purchases and the 'total' amount spent.
        Example:
        {
            "user123": {"count": 2, "total": 150},
            "user456": {"count": 1, "total": 75}
        }
    """
    user_index: dict[str, dict[str, int]] = {}

    for event in events:
        # Ensure the event is a dictionary before processing
        if not isinstance(event, dict):
            continue

        # Safely get event attributes
        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        # Validate the event data according to the requirements
        if (
            kind == "purchase"
            and isinstance(user_id, str)
            and user_id  # Ensures user_id is a non-empty string
            and isinstance(amount, int)
        ):
            # If the user is not yet in the index, initialize their record.
            if user_id not in user_index:
                user_index[user_id] = {"count": 0, "total": 0}

            # Update the user's purchase statistics.
            user_index[user_id]["count"] += 1
            user_index[user_id]["total"] += amount

    return user_index
