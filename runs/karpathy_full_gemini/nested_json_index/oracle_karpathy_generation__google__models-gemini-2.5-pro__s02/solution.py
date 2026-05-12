from collections import defaultdict
from typing import Any, Dict, List

def build_user_purchase_index(
    events: List[Dict[str, Any]]
) -> Dict[str, Dict[str, int]]:
    """
    Builds an index of user purchases from a list of events.

    This function processes a list of event dictionaries, filtering for valid
    "purchase" events. A valid purchase event must have:
    - "kind" equal to "purchase"
    - "user_id" as a non-empty string
    - "amount" as an integer

    The input list and its contained dictionaries are not mutated.

    Args:
        events: A list of dictionaries, where each dictionary represents an event.
                Each event may contain 'user_id', 'kind', and 'amount' keys.

    Returns:
        A dictionary where keys are user_ids and values are dictionaries
        containing the 'count' of purchases and the 'total' amount spent.
        Example: {'user_123': {'count': 2, 'total': 150}}
    """
    user_index: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {"count": 0, "total": 0}
    )

    for event in events:
        kind = event.get("kind")
        user_id = event.get("user_id")
        amount = event.get("amount")

        # An event is included only if it is a purchase by a valid user
        # with a valid purchase amount.
        if (
            kind == "purchase"
            and isinstance(user_id, str)
            and user_id
            and isinstance(amount, int)
        ):
            user_index[user_id]["count"] += 1
            user_index[user_id]["total"] += amount

    return dict(user_index)
