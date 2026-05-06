"""
event_windows.py

Groups events into fixed-size time windows and summarises each window.
"""

from collections import defaultdict
import math


def _is_valid_event(event: dict) -> bool:
    """Return True when the event has integer 'timestamp' and 'value' fields."""
    if not isinstance(event, dict):
        return False
    timestamp = event.get("timestamp")
    value = event.get("value")
    return isinstance(timestamp, int) and isinstance(value, int)


def _window_key(timestamp: int, window_size: int) -> int:
    """Return the floor-division bucket index for a timestamp."""
    return math.floor(timestamp / window_size)


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Summarise events grouped into half-open windows of length window_size.

    Parameters
    ----------
    events : list[dict]
        Each element should contain integer fields 'timestamp' and 'value'.
        Malformed elements are silently skipped.
    window_size : int
        Width of each window.  Must be a positive integer.

    Returns
    -------
    list[dict]
        One dict per non-empty window, sorted by 'start', with keys
        'start', 'count', and 'total'.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not _is_valid_event(event):
            continue
        key = _window_key(event["timestamp"], window_size)
        counts[key] += 1
        totals[key] += event["value"]

    return [
        {
            "start": key * window_size,
            "count": counts[key],
            "total": totals[key],
        }
        for key in sorted(counts)
    ]
