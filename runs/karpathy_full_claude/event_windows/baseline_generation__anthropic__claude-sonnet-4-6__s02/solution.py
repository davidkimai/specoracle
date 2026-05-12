"""
event_windows.py

Implements summarize_windows for grouping events into fixed-size time windows.
"""

from __future__ import annotations

import math
from collections import defaultdict


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Group events into half-open windows [k * window_size, (k+1) * window_size).

    Parameters
    ----------
    events : list[dict]
        Each event should have integer "timestamp" and "value" fields.
        Malformed events (missing keys, non-integer values) are silently ignored.
    window_size : int
        The size of each window. Must be a positive integer.

    Returns
    -------
    list[dict]
        Sorted list of dicts with keys "start", "count", and "total".

    Raises
    ------
    ValueError
        If window_size is not positive.
    """
    if not isinstance(window_size, int) or isinstance(window_size, bool):
        raise ValueError("window_size must be a positive integer")
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    # counts[k] = [count, total]
    window_data: dict[int, list[int]] = defaultdict(lambda: [0, 0])

    for event in events:
        if not isinstance(event, dict):
            continue
        try:
            timestamp = event["timestamp"]
            value = event["value"]
        except (KeyError, TypeError):
            continue

        # Validate that both fields are integers (bool is excluded)
        if (
            not isinstance(timestamp, int)
            or isinstance(timestamp, bool)
            or not isinstance(value, int)
            or isinstance(value, bool)
        ):
            continue

        k = math.floor(timestamp / window_size)
        window_data[k][0] += 1
        window_data[k][1] += value

    result = []
    for k in sorted(window_data.keys()):
        count, total = window_data[k]
        result.append({
            "start": k * window_size,
            "count": count,
            "total": total,
        })

    return result
