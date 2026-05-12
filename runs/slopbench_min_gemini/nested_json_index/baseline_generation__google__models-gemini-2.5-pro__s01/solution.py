"""
A module for indexing user purchase events from a list of event dictionaries.
"""

import collections
from typing import Any, Dict, List

def build_user_purchase_index(
    events: List[Dict[str, Any]]
) -> Dict[str, Dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    This function processes a list of event dictionaries, filtering for valid
    "purchase" events. A valid purchase event must have:
    - "kind" with the value "purchase"
    - "user_id" with a non-empty string value
    - "amount" with an integer value

    The function returns a dictionary where each key is a user_id. The
    corresponding value is another dictionary containing the total count of
    purchases and the total amount spent by that user.

    The input list and its contained dictionaries are not mutated.

    Args:
        events: A list of dictionaries, where each dictionary represents an event.

    Returns:
        A dictionary mapping each user_id to an object containing their
        total purchase count and total purchase amount.
        Example:
        {
            "user123": {"count": 2, "total": 150},
            "user456": {"count": 1, "total": 75}
        }
    """
    user_purchase_index: Dict[str, Dict[str, int]] = collections.defaultdict(
        lambda: {"count": 0, "total": 0}
    )

    for event in events:
        # Ensure event is a dictionary to prevent attribute errors
        if not isinstance(event, dict):
            continue

        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        # Validate the event's data types and values
        if (
            kind == "purchase"
            and isinstance(user_id, str)
            and user_id  # Ensures user_id is not an empty string
            and isinstance(amount, int)
        ):
            # Update the index for the given user_id
            user_purchase_index[user_id]["count"] += 1
            user_purchase_index[user_id]["total"] += amount

    # Convert defaultdict to a standard dict for the return value
    return dict(user_purchase_index)
