"""
event_windows.py

Provides summarize_windows for grouping events into fixed-size time windows.
"""

from collections import defaultdict
from math import floor


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Group events into half-open windows [k*window_size, (k+1)*window_size).

    Parameters
    ----------
    events : list[dict]
        Each event should have integer fields "timestamp" and "value".
        Malformed events (missing or non-integer fields) are silently ignored.
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
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    # Accumulate count and total per window key k
    window_counts: dict[int, int] = defaultdict(int)
    window_totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not isinstance(event, dict):
            continue
        timestamp = event.get("timestamp")
        value = event.get("value")
        # Both fields must be present and be integers (bool excluded)
        if (
            not isinstance(timestamp, int)
            or isinstance(timestamp, bool)
            or not isinstance(value, int)
            or isinstance(value, bool)
        ):
            continue

        k = floor(timestamp / window_size)
        window_counts[k] += 1
        window_totals[k] += value

    result = []
    for k in sorted(window_counts.keys()):
        start = k * window_size
        result.append(
            {
                "start": start,
                "count": window_counts[k],
                "total": window_totals[k],
            }
        )

    return result
