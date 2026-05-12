"""
A module for summarizing events into time windows.
"""

import collections
from typing import List, Dict, Any

def summarize_windows(events: List[Dict[str, Any]], window_size: int) -> List[Dict[str, Any]]:
    """
    Groups events into time windows and calculates summaries for each window.

    Each event is a dictionary expected to have "timestamp" and "value" integer
    fields. Malformed events (e.g., not a dict, missing keys, or non-integer
    values) are ignored.

    Events are grouped into half-open windows of the form
    [k * window_size, (k + 1) * window_size) based on their timestamp.

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of dictionaries, each representing a summarized window,
        sorted by the window start time. Each dictionary contains the
        "start" of the window, the "count" of events in it, and the "total"
        sum of their values.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    # Use a defaultdict to simplify the aggregation logic.
    # The key is the window start timestamp, and the value is a dict for aggregates.
    window_aggregates = collections.defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        # Validate event structure and types, ignoring malformed ones.
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not (isinstance(timestamp, int) and isinstance(value, int)):
            continue

        # Calculate the start of the window for the event's timestamp
        # using integer floor division.
        window_start = (timestamp // window_size) * window_size

        # Update aggregates for the corresponding window.
        window_aggregates[window_start]["count"] += 1
        window_aggregates[window_start]["total"] += value

    # Format the output as a sorted list of dictionaries.
    # Sorting by the dictionary keys (window start times) ensures the
    # output is ordered as required.
    result = [
        {
            "start": start,
            "count": summary["count"],
            "total": summary["total"],
        }
        for start, summary in sorted(window_aggregates.items())
    ]

    return result
