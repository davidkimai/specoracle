"""
event_windows.py

Provides summarize_windows(events, window_size) -> list[dict].
"""

from collections import defaultdict
from math import floor


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Group events into fixed-size time windows and return summary statistics.

    Parameters
    ----------
    events : list[dict]
        Each element should have integer fields "timestamp" and "value".
        Malformed events (missing fields, non-integer values) are silently ignored.
    window_size : int
        The width of each window. Must be a positive integer.

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

    # Accumulate per-window statistics
    # key: window start (int), value: [count, total]
    windows: dict[int, list[int]] = defaultdict(lambda: [0, 0])

    for event in events:
        # Validate that event is a dict with integer "timestamp" and "value"
        if not isinstance(event, dict):
            continue
        timestamp = event.get("timestamp")
        value = event.get("value")
        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue
        # Booleans are subclasses of int in Python; treat them as malformed
        if isinstance(timestamp, bool) or isinstance(value, bool):
            continue

        window_start = (timestamp // window_size) * window_size
        windows[window_start][0] += 1
        windows[window_start][1] += value

    result = [
        {"start": start, "count": stats[0], "total": stats[1]}
        for start, stats in sorted(windows.items())
    ]
    return result
