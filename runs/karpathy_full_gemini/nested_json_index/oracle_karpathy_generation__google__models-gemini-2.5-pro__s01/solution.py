"""
A module for indexing user purchase events.
"""

import collections
from typing import Dict, List, Any

def build_user_purchase_index(events: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    Aggregates purchase events from a list to build a user-keyed index.

    Filters events to include only those where 'kind' is 'purchase', 'user_id'
    is a non-empty string, and 'amount' is an integer. The returned index maps
    each user_id to a dictionary containing their total purchase 'count' and
    the 'total' sum of purchase amounts.

    The input list and its contained dictionaries are not mutated.

    Args:
        events: A list of event dictionaries, where each dictionary may contain
                "user_id", "kind", and "amount" keys.

    Returns:
        A dictionary mapping user IDs to their aggregated purchase data.
        Returns an empty dictionary if no valid purchase events are found.
    """
    user_purchase_index: Dict[str, Dict[str, int]] = collections.defaultdict(
        lambda: {"count": 0, "total": 0}
    )

    for event in events:
        if not isinstance(event, dict):
            continue

        # Filter for valid purchase events based on specified criteria.
        if event.get("kind") != "purchase":
            continue

        user_id = event.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            continue

        amount = event.get("amount")
        if not isinstance(amount, int):
            continue

        # Aggregate statistics for the valid user.
        stats = user_purchase_index[user_id]
        stats["count"] += 1
        stats["total"] += amount

    return dict(user_purchase_index)
