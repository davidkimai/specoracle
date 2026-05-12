"""
This module provides a function to index user purchase events.
"""

from typing import Any, Dict, List


def build_user_purchase_index(
    events: List[Dict[str, Any]]
) -> Dict[str, Dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    This function processes a list of event dictionaries, filtering for valid
    purchase events and aggregating the data by user_id. The input list and
    its contained dictionaries are not mutated.

    Args:
        events: A list of event dictionaries. Each event may contain 'user_id',
                'kind', and 'amount'.

    Returns:
        A dictionary where keys are user_ids. Each value is a dictionary
        containing the total purchase count and total purchase amount for
        that user, structured as {"count": purchase_count, "total": total_amount}.
        Events are included in the index only if all of the following are true:
        - The event 'kind' is the string "purchase".
        - The 'user_id' is a non-empty string.
        - The 'amount' is an integer.
    """
    purchase_index: Dict[str, Dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        # An event is a valid purchase if it has the correct kind, a non-empty
        # string user_id, and an integer amount.
        if (
            kind == "purchase"
            and isinstance(user_id, str)
            and user_id
            and isinstance(amount, int)
        ):
            # If the user is not yet in the index, initialize their record.
            if user_id not in purchase_index:
                purchase_index[user_id] = {"count": 0, "total": 0}

            # Update the user's purchase statistics.
            purchase_index[user_id]["count"] += 1
            purchase_index[user_id]["total"] += amount

    return purchase_index
