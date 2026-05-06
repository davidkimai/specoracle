"""
event_windows.py

Provides summarize_windows(events, window_size) which groups events into
fixed-size time windows and returns summary statistics per window.
"""

from math import floor
from collections import defaultdict


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Summarize events into non-overlapping windows of size window_size.

    Parameters
    ----------
    events : list[dict]
        Each event should have integer fields "timestamp" and "value".
        Malformed events (missing fields, non-integer values) are ignored.
    window_size : int
        Width of each window. Must be a positive integer.

    Returns
    -------
    list[dict]
        Sorted list of dicts with keys "start", "count", and "total".

    Raises
    ------
    ValueError
        If window_size is not positive.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    # accumulate per-window stats
    window_totals: dict[int, int] = defaultdict(int)
    window_counts: dict[int, int] = defaultdict(int)

    for event in events:
        # skip non-dict entries
        if not isinstance(event, dict):
            continue

        # validate required fields
        try:
            timestamp = event["timestamp"]
            value = event["value"]
        except (KeyError, TypeError):
            continue

        # ensure both are integers (bool is a subclass of int; treat as valid)
        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        window_key = (timestamp // window_size) * window_size
        window_counts[window_key] += 1
        window_totals[window_key] += value

    result = [
        {"start": start, "count": window_counts[start], "total": window_totals[start]}
        for start in sorted(window_counts)
    ]

    return result
