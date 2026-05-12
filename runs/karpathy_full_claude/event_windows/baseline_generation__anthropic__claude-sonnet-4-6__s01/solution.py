"""
event_windows.py

Provides summarize_windows for grouping events into fixed-size time windows.
"""

from collections import defaultdict


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Summarize events into half-open windows of size `window_size`.

    Parameters
    ----------
    events : list[dict]
        Each event should have integer "timestamp" and "value" fields.
        Malformed events (missing fields, non-integer values) are ignored.
    window_size : int
        Must be a positive integer. Raises ValueError otherwise.

    Returns
    -------
    list[dict]
        Sorted list of dicts with keys "start", "count", and "total".
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not isinstance(event, dict):
            continue
        try:
            timestamp = event["timestamp"]
            value = event["value"]
        except KeyError:
            continue
        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue
        # Booleans are subclasses of int; treat them as malformed
        if isinstance(timestamp, bool) or isinstance(value, bool):
            continue

        window_key = (timestamp // window_size) * window_size
        counts[window_key] += 1
        totals[window_key] += value

    result = [
        {"start": start, "count": counts[start], "total": totals[start]}
        for start in sorted(counts)
    ]
    return result
