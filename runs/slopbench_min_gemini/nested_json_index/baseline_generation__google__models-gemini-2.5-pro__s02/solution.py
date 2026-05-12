"""
A module for indexing user purchase events from a list of event data.
"""

# This module uses standard library features and does not require third-party imports.
# Type hints are compatible with Python 3.9+ as per the task specification.

def build_user_purchase_index(events: list[dict]) -> dict[str, dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    This function processes a list of event dictionaries, filtering for valid
    purchase events and aggregating purchase counts and total amounts for each user.

    An event is considered a valid purchase if it meets all the following criteria:
    - It contains a "kind" key with the string value "purchase".
    - It contains a "user_id" key with a non-empty string value.
    - It contains an "amount" key with an integer value.

    Events that do not meet these criteria are ignored. The input list and its
    contained dictionaries are not mutated.

    Args:
        events: A list of dictionaries, where each dictionary represents an event.
                Each event may contain "user_id", "kind", and "amount" keys.

    Returns:
        A dictionary where keys are user_id strings and values are dictionaries
        containing the total purchase count and total purchase amount for that user.
        Example:
        {
            "user123": {"count": 2, "total": 150},
            "user456": {"count": 1, "total": 75}
        }
    """
    purchase_index: dict[str, dict[str, int]] = {}

    for event in events:
        # Ensure the event is a dictionary to safely use .get()
        if not isinstance(event, dict):
            continue

        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        # Validate that the event is a well-formed purchase event according to
        # the specified requirements.
        if (
            kind == "purchase"
            and isinstance(user_id, str)
            and user_id  # This checks for non-empty string
            and isinstance(amount, int)
        ):
            # Retrieve or initialize the stats dictionary for the user.
            # Using str.setdefault is an efficient way to handle new keys.
            user_stats = purchase_index.setdefault(user_id, {"count": 0, "total": 0})

            # Update the count and total amount for the user.
            user_stats["count"] += 1
            user_stats["total"] += amount

    return purchase_index
