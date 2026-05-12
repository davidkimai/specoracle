"""A module for summarizing event data into time windows."""

import collections
from typing import Any, Dict, List


def _is_valid_event(event: Any) -> bool:
    """
    Checks if an event is well-formed.

    A valid event is a dictionary containing integer "timestamp" and "value" keys.

    Args:
        event: The event to validate.

    Returns:
        True if the event is valid, False otherwise.
    """
    if not isinstance(event, dict):
        return False

    if not isinstance(event.get("timestamp"), int):
        return False

    if not isinstance(event.get("value"), int):
        return False

    return True


def summarize_windows(events: List[Dict], window_size: int) -> List[Dict]:
    """
    Groups events into time windows and calculates summaries for each window.

    Each event is expected to be a dictionary with "timestamp" and "value"
    integer fields. Malformed events are ignored.

    The windows are half-open intervals of the form:
    [k * window_size, (k + 1) * window_size)

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of summary dictionaries, sorted by window start time. Each
        summary includes the window start, the count of events, and the
        total of their values.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    # The key is the window start time, and the value is a dict for aggregates.
    summaries = collections.defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        if not _is_valid_event(event):
            continue

        # We can now safely access keys as they are validated by _is_valid_event.
        timestamp: int = event["timestamp"]
        value: int = event["value"]

        start = (timestamp // window_size) * window_size

        summaries[start]["count"] += 1
        summaries[start]["total"] += value

    # Format the summaries into the required list of dictionaries.
    result = [
        {"start": start, "count": data["count"], "total": data["total"]}
        for start, data in summaries.items()
    ]

    # Sort the results by the window start time.
    result.sort(key=lambda item: item["start"])

    return result
