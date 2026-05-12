"""
This module provides a function to summarize time-series events into windows.
"""

import collections
from typing import List, Dict, Any


def _is_valid_event(event: Any) -> bool:
    """
    Checks if an event is a dictionary with integer 'timestamp' and 'value'.

    Args:
        event: The event to validate.

    Returns:
        True if the event is valid, False otherwise.
    """
    if not isinstance(event, dict):
        return False

    timestamp = event.get("timestamp")
    if not isinstance(timestamp, int):
        return False

    value = event.get("value")
    if not isinstance(value, int):
        return False

    return True


def _format_summaries(
    summaries: Dict[int, Dict[str, int]]
) -> List[Dict[str, int]]:
    """
    Converts the summaries dictionary to a sorted list of summary rows.

    Args:
        summaries: A dictionary mapping window start times to summary data.

    Returns:
        A list of summary dictionaries, sorted by the window start time.
    """
    return [
        {
            "start": start,
            "count": summaries[start]["count"],
            "total": summaries[start]["total"],
        }
        for start in sorted(summaries)
    ]


def summarize_windows(
    events: List[Dict[str, Any]], window_size: int
) -> List[Dict[str, int]]:
    """
    Groups events into fixed-size time windows and computes summaries.

    Each event is placed into a half-open window of `[start, start + window_size)`
    based on its timestamp. Malformed events are ignored.

    Args:
        events: A list of event dictionaries. Each valid event must have
                'timestamp' and 'value' integer fields.
        window_size: The positive integer size of each time window.

    Returns:
        A list of summary dictionaries, sorted by window start time.
        Each dictionary contains 'start', 'count' of events, and 'total'
        sum of event values for that window.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    window_summaries = collections.defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        if not _is_valid_event(event):
            continue

        timestamp = event["timestamp"]
        value = event["value"]

        start = (timestamp // window_size) * window_size

        summary = window_summaries[start]
        summary["count"] += 1
        summary["total"] += value

    return _format_summaries(window_summaries)
