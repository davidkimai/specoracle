"""
event_windows.py

Groups events into fixed-size time windows and returns summary statistics.
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


def _window_key(timestamp: int, window_size: int) -> int:
    """Return the start of the window that contains the given timestamp."""
    return math.floor(timestamp / window_size) * window_size


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Summarize events grouped into half-open windows of size window_size.

    Parameters
    ----------
    events:
        A list of dicts, each expected to have integer 'timestamp' and 'value'.
        Malformed events are silently ignored.
    window_size:
        Positive integer defining the width of each window.

    Returns
    -------
    A list of dicts sorted by window start, each containing:
        - 'start':  the inclusive start of the window
        - 'count':  number of valid events in the window
        - 'total':  sum of 'value' for events in the window
    """
    if not isinstance(window_size, int) or isinstance(window_size, bool):
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")

    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not _is_valid_event(event):
            continue
        start = _window_key(event["timestamp"], window_size)
        counts[start] += 1
        totals[start] += event["value"]

    return [
        {"start": start, "count": counts[start], "total": totals[start]}
        for start in sorted(counts)
    ]
