"""
event_windows: group events into fixed-size time windows and summarize them.
"""

from __future__ import annotations

import math
from collections import defaultdict


def _is_valid_event(event: dict) -> bool:
    """Return True if the event has integer 'timestamp' and 'value' fields."""
    if not isinstance(event, dict):
        return False
    timestamp = event.get("timestamp")
    value = event.get("value")
    return isinstance(timestamp, int) and isinstance(value, int)


def _window_start(timestamp: int, window_size: int) -> int:
    """Return the start of the window containing timestamp."""
    return math.floor(timestamp / window_size) * window_size


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Summarize events into half-open time windows of size window_size.

    Args:
        events: list of dicts, each with integer 'timestamp' and 'value'.
        window_size: positive integer defining the width of each window.

    Returns:
        List of dicts sorted by window start, each containing:
            - 'start': window start (inclusive)
            - 'count': number of events in the window
            - 'total': sum of values in the window

    Raises:
        ValueError: if window_size is not positive.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not _is_valid_event(event):
            continue
        start = _window_start(event["timestamp"], window_size)
        counts[start] += 1
        totals[start] += event["value"]

    return [
        {"start": start, "count": counts[start], "total": totals[start]}
        for start in sorted(counts)
    ]
