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
    Group events into half-open windows [k * window_size, (k + 1) * window_size).

    Parameters
    ----------
    events : list[dict]
        Each event should have integer "timestamp" and "value" fields.
        Malformed events (missing fields, non-integer values) are ignored.
    window_size : int
        The size of each window. Must be a positive integer.

    Returns
    -------
    list[dict]
        List of dicts with keys "start", "count", and "total", sorted by "start".

    Raises
    ------
    ValueError
        If window_size is not positive.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    # Accumulate per-window statistics
    # key: window start (k * window_size)
    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not isinstance(event, dict):
            continue
        try:
            timestamp = event["timestamp"]
            value = event["value"]
        except (KeyError, TypeError):
            continue

        # Validate that both fields are integers (bool is a subclass of int; exclude it)
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            continue
        if not isinstance(value, int) or isinstance(value, bool):
            continue

        k = math.floor(timestamp / window_size)
        start = k * window_size

        counts[start] += 1
        totals[start] += value

    result = [
        {"start": start, "count": counts[start], "total": totals[start]}
        for start in sorted(counts)
    ]
    return result
