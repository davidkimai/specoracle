"""
A module for summarizing event data into time-based windows.
"""

import collections
from typing import Any, Dict, List


def summarize_windows(
    events: List[Dict[str, Any]], window_size: int
) -> List[Dict[str, int]]:
    """
    Groups events into time windows and calculates count and total value for each.

    The function processes a list of event dictionaries, each expected to have
    "timestamp" and "value" integer fields. It groups these events into
    half-open time windows of a specified size, defined by the interval
    [k * window_size, (k + 1) * window_size).

    For each window that contains at least one event, it computes the total
    number of events (count) and the sum of their values (total).

    Args:
        events: A list of event dictionaries. Each valid event should have
                "timestamp" and "value" integer fields. Malformed events
                (e.g., not a dict, missing keys, non-integer values) are
                ignored.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of dictionaries, each representing a summary for a non-empty
        window. Each summary dictionary contains "start" (the timestamp at
        the beginning of the window), "count", and "total". The list is
        sorted in ascending order by the window start time.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    window_summaries = collections.defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not (isinstance(timestamp, int) and isinstance(value, int)):
            continue

        window_start = (timestamp // window_size) * window_size

        summary = window_summaries[window_start]
        summary["count"] += 1
        summary["total"] += value

    result = [
        {
            "start": start,
            "count": summary["count"],
            "total": summary["total"],
        }
        for start, summary in window_summaries.items()
    ]

    result.sort(key=lambda item: item["start"])

    return result
