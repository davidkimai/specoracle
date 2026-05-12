"""
Module for indexing user purchase events from a stream of event data.
"""

from typing import Any, Dict, List, Optional, Tuple


def _parse_purchase_event(event: Dict[str, Any]) -> Optional[Tuple[str, int]]:
    """
    Parses a valid purchase event, returning key data if valid.

    An event is a valid purchase if it is a dictionary containing:
    - "kind": "purchase"
    - "user_id": a non-empty string
    - "amount": an integer

    Args:
        event: The event dictionary to parse.

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
    if not isinstance(amount, int):
        return None

    return user_id, amount


def build_user_purchase_index(
    events: List[Dict[str, Any]]
) -> Dict[str, Dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    The index is a dictionary mapping user_id to their purchase statistics.
    Each statistic dictionary contains the total count of purchases and the
    sum of purchase amounts.

    Events that do not represent valid purchases are ignored.

    Args:
        events: A list of event dictionaries.

    Returns:
        A dictionary where keys are user_ids and values are dictionaries
        containing 'count' and 'total' purchase information.

    Raises:
        TypeError: If the input `events` is not a list.
    """
    if not isinstance(events, list):
        raise TypeError("Input 'events' must be a list.")

    index: Dict[str, Dict[str, int]] = {}

    for event in events:
        purchase_data = _parse_purchase_event(event)
        if purchase_data is None:
            continue

        user_id, amount = purchase_data

        user_stats = index.setdefault(user_id, {"count": 0, "total": 0})
        user_stats["count"] += 1
        user_stats["total"] += amount

    return index
