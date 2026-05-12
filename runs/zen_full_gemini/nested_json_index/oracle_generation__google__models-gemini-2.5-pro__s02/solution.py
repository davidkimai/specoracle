"""
Processes event data to build an index of user purchases.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


def _parse_purchase_event(event: Any) -> Optional[Tuple[str, int]]:
    """
    Validates and extracts data from a potential purchase event.

    An event is considered a valid purchase if it is a dictionary containing:
    - "kind": The string "purchase"
    - "user_id": A non-empty string
    - "amount": An integer (but not a boolean)

    Args:
        event: An object, expected to be a dictionary representing an event.

    Returns:
        A tuple of (user_id, amount) if the event is a valid purchase,
        otherwise None.
    """
    if not isinstance(event, dict):
        return None

    if event.get("kind") != "purchase":
        return None

    user_id = event.get("user_id")
    if not isinstance(user_id, str) or not user_id:
        return None

    amount = event.get("amount")
    # In Python, bool is a subclass of int, so we must explicitly exclude it.
    if not isinstance(amount, int) or isinstance(amount, bool):
        return None

    return user_id, amount


def build_user_purchase_index(
    events: List[Dict[str, Any]]
) -> Dict[str, Dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    This function processes a list of event dictionaries, filtering for valid
    purchase events and aggregating the results by user.

    Args:
        events: A list of dictionaries, where each dictionary represents an event.

    Returns:
        A dictionary where keys are user IDs and values are dictionaries
        containing the total purchase count and total purchase amount for that user.
        Example: {"user1": {"count": 2, "total": 150}}

    Raises:
        TypeError: If the input `events` is not a list.
    """
    if not isinstance(events, list):
        raise TypeError("Input 'events' must be a list.")

    purchase_index = defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        parsed_data = _parse_purchase_event(event)
        if parsed_data is None:
            continue

        user_id, amount = parsed_data

        user_summary = purchase_index[user_id]
        user_summary["count"] += 1
        user_summary["total"] += amount

    return dict(purchase_index)
