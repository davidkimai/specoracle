"""
event_windows.py

Provides summarize_windows for grouping events into fixed-size time windows.
"""

from collections import defaultdict


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Summarize events into half-open windows of size window_size.

    Parameters
    ----------
    events : list[dict]
        Each dict should have integer "timestamp" and "value" fields.
        Malformed events (missing keys, non-integer values) are ignored.
    window_size : int
        Width of each window. Must be positive.

    Returns
    -------
    list[dict]
        Sorted list of {"start": int, "count": int, "total": int} dicts,
        one per non-empty window.

    Raises
    ------
    ValueError
        If window_size is not positive.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    # Each bucket: [count, total]
    buckets: dict[int, list[int]] = defaultdict(lambda: [0, 0])

    for event in events:
        # Validate event structure
        if not isinstance(event, dict):
            continue
        try:
            timestamp = event["timestamp"]
            value = event["value"]
        except (KeyError, TypeError):
            continue

        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        # Booleans are subclasses of int; treat them as malformed
        if isinstance(timestamp, bool) or isinstance(value, bool):
            continue

        window_start = (timestamp // window_size) * window_size
        buckets[window_start][0] += 1
        buckets[window_start][1] += value

    result = [
        {"start": start, "count": bucket[0], "total": bucket[1]}
        for start, bucket in sorted(buckets.items())
    ]
    return result
