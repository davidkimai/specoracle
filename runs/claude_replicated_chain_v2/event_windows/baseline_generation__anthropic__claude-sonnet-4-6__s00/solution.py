"""
event_windows.py

Implements summarize_windows for grouping events into fixed-size time windows.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Group events into half-open windows [k * window_size, (k+1) * window_size).

    Parameters
    ----------
    events : list[dict]
        Each event should have integer fields "timestamp" and "value".
        Malformed events (missing or non-integer fields) are silently ignored.
    window_size : int
        The width of each window. Must be a positive integer.

    Returns
    -------
    list[dict]
        A list of dicts, each with keys "start", "count", and "total",
        sorted ascending by "start".

    Raises
    ------
    ValueError
        If window_size is not positive.
    """
    if not isinstance(window_size, int) or isinstance(window_size, bool):
        raise ValueError("window_size must be a positive integer")
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    # Accumulate count and total per window key k
    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not isinstance(event, dict):
            continue
        ts = event.get("timestamp")
        val = event.get("value")
        # Both fields must be present and be integers (not booleans)
        if (
            ts is None
            or val is None
            or isinstance(ts, bool)
            or isinstance(val, bool)
            or not isinstance(ts, int)
            or not isinstance(val, int)
        ):
            continue
        k = math.floor(ts / window_size)
        counts[k] += 1
        totals[k] += val

    result = []
    for k in sorted(counts.keys()):
        start = k * window_size
        result.append(
            {
                "start": start,
                "count": counts[k],
                "total": totals[k],
            }
        )

    return result
