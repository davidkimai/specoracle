import collections

def _is_valid_purchase_event(event: dict) -> bool:
    """
    Checks if an event dictionary represents a valid purchase.

    A valid purchase must:
    - Be a dictionary.
    - Have a "kind" of "purchase".
    - Have a non-empty string "user_id".
    - Have an integer "amount".

    Args:
        event: The event dictionary to validate.

    Returns:
        True if the event is a valid purchase, False otherwise.
    """
    if not isinstance(event, dict):
        return False

    if event.get("kind") != "purchase":
        return False

    user_id = event.get("user_id")
    if not isinstance(user_id, str) or not user_id:
        return False

    amount = event.get("amount")
    if not isinstance(amount, int):
        return False

    return True


def build_user_purchase_index(
    events: list[dict],
) -> dict[str, dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    The index aggregates the count of purchases and the total amount spent
    for each user.

    Only events that are valid purchases are included. A valid purchase event
    is a dictionary with:
    - "kind": "purchase"
    - "user_id": a non-empty string
    - "amount": an integer

    Args:
        events: A list of event dictionaries.

    Returns:
        A dictionary where keys are user_ids and values are dictionaries
        containing the 'count' of purchases and the 'total' amount.
        Example: {'user1': {'count': 2, 'total': 150}}

    Raises:
        TypeError: If the 'events' argument is not a list.
    """
    if not isinstance(events, list):
        raise TypeError("Input 'events' must be a list of dictionaries.")

    index: collections.defaultdict[str, dict[str, int]] = collections.defaultdict(
        lambda: {"count": 0, "total": 0}
    )

    for event in events:
        if _is_valid_purchase_event(event):
            # We can safely access keys now because validation passed.
            user_id = event["user_id"]
            amount = event["amount"]

            user_summary = index[user_id]
            user_summary["count"] += 1
            user_summary["total"] += amount

    return dict(index)
