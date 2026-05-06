"""
event_windows module: provides summarize_windows for grouping events into time windows.
"""

from math import floor
from collections import defaultdict


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Summarize events into fixed-size time windows.

    Parameters
    ----------
    events : list[dict]
        Each event should have integer fields "timestamp" and "value".
        Malformed events (missing fields, non-integer values) are ignored.
    window_size : int
        The size of each window. Must be a positive integer.

    Returns
    -------
    list[dict]
        A list of dicts with keys "start", "count", and "total", sorted by
        window start (ascending).

    Raises
    ------
    ValueError
        If window_size is not positive.
    """
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size!r}")

    # accumulate count and total per window key
    window_count = defaultdict(int)
    window_total = defaultdict(int)

    for event in events:
        if not isinstance(event, dict):
            continue
        try:
            timestamp = event["timestamp"]
            value = event["value"]
        except (KeyError, TypeError):
            continue

        # Ensure both fields are integers (bool is a subclass of int, treat as int)
        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        # Compute the window key using integer floor division
        k = timestamp // window_size
        start = k * window_size

        window_count[start] += 1
        window_total[start] += value

    # Build result sorted by window start
    result = [
        {"start": start, "count": window_count[start], "total": window_total[start]}
        for start in sorted(window_count)
    ]

    return result
