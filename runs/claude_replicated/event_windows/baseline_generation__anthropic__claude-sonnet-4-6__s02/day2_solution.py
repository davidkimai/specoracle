"""
event_windows.py

Implements summarize_windows for grouping events into fixed-size time windows.
"""

from collections import defaultdict


def summarize_windows(events: list[dict], window_size: int, *, include_average: bool = False) -> list[dict]:
    """
    Group events into half-open windows [k * window_size, (k + 1) * window_size).

    Parameters
    ----------
    events : list[dict]
        Each event should have integer "timestamp" and "value" fields.
        Malformed events (missing or non-integer fields) are silently ignored.
    window_size : int
        The size of each window. Must be a positive integer.
    include_average : bool, optional
        When True, each returned row includes an "average" field equal to
        total / count. Defaults to False.

    Returns
    -------
    list[dict]
        A list of dicts sorted by window start, each containing:
            - "start"   : int   – the window's starting timestamp
            - "count"   : int   – number of events in the window
            - "total"   : int   – sum of "value" for events in the window
            - "average" : float – total / count (only when include_average=True)
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    # Accumulate count and total per window key k
    window_count: dict[int, int] = defaultdict(int)
    window_total: dict[int, int] = defaultdict(int)

    for event in events:
        # Validate event structure
        if not isinstance(event, dict):
            continue
        timestamp = event.get("timestamp")
        value = event.get("value")
        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue
        # Exclude booleans (bool is a subclass of int in Python)
        if isinstance(timestamp, bool) or isinstance(value, bool):
            continue

        k = timestamp // window_size
        window_count[k] += 1
        window_total[k] += value

    result = []
    for k in sorted(window_count.keys()):
        start = k * window_size
        count = window_count[k]
        total = window_total[k]
        row = {
            "start": start,
            "count": count,
            "total": total,
        }
        if include_average:
            row["average"] = total / count
        result.append(row)

    return result
