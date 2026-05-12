"""
A module for summarizing event data into time windows.
"""

from typing import Dict, List


def summarize_windows(events: List[Dict], window_size: int) -> List[Dict]:
    """
    Summarizes events into fixed-size, non-overlapping time windows.

    Each event is a dictionary expected to have integer "timestamp" and "value"
    fields. Events that are not dictionaries or lack these fields with integer
    values are considered malformed and ignored.

    Events are grouped into half-open windows of [start, start + window_size)
    based on their timestamp. The start of each window is a multiple of
    `window_size`.

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of dictionaries, each summarizing a window. Each dictionary
        contains "start" (the window's start timestamp), "count" (the number
        of events in the window), and "total" (the sum of values of events
        in the window). The list is sorted by the window start time.

    Raises:
        ValueError: If `window_size` is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    window_summaries: Dict[int, Dict[str, int]] = {}

    for event in events:
        # Validate event structure and types
        if not isinstance(event, dict):
            continue
        timestamp = event.get("timestamp")
        value = event.get("value")
        if not (isinstance(timestamp, int) and isinstance(value, int)):
            continue

        # Calculate the start of the window
        start = (timestamp // window_size) * window_size

        # Aggregate event data into the corresponding window
        if start not in window_summaries:
            window_summaries[start] = {"count": 0, "total": 0}

        window_summaries[start]["count"] += 1
        window_summaries[start]["total"] += value

    # Format the aggregated data into the required output list, sorted by start time
    result = [
        {
            "start": start,
            "count": summary["count"],
            "total": summary["total"],
        }
        for start, summary in sorted(window_summaries.items())
    ]

    return result
