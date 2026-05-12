"""
A module for summarizing event data into time-based windows.
"""

import collections
from typing import Any, Dict, List


def _is_valid_event(event: Any) -> bool:
    """
    Checks if an event is a dictionary with integer 'timestamp' and 'value'.

    Args:
        event: The object to validate.

    Returns:
        True if the event is valid, False otherwise.
    """
    if not isinstance(event, dict):
        return False

    timestamp = event.get("timestamp")
    value = event.get("value")

    if not isinstance(timestamp, int) or not isinstance(value, int):
        return False

    return True


def summarize_windows(
    events: List[Dict[str, Any]], window_size: int
) -> List[Dict[str, int]]:
    """
    Groups events into windows and computes summaries for each window.

    Each event is a dictionary with "timestamp" and "value" integer fields.
    Malformed events are ignored. Windows are half-open intervals of the form
    [k * window_size, (k + 1) * window_size).

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of summary dictionaries, sorted by window start time. Each
        summary has "start", "count", and "total" fields.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    window_aggregates = collections.defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        if not _is_valid_event(event):
            continue

        timestamp = event["timestamp"]
        value = event["value"]

        # Integer floor division determines the window's starting bucket.
        # The window start is the beginning of that bucket's time range.
        window_start = (timestamp // window_size) * window_size

        window_aggregates[window_start]["count"] += 1
        window_aggregates[window_start]["total"] += value

    # Format the aggregated data into the required list of dictionaries.
    result = [
        {
            "start": start,
            "count": data["count"],
            "total": data["total"],
        }
        for start, data in window_aggregates.items()
    ]

    # Sort the results by the window start time for predictable output.
    result.sort(key=lambda item: item["start"])

    return result
