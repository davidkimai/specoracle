"""
event_windows: group timestamped events into fixed-size windows.
"""

from math import floor
from collections import defaultdict


def _is_valid(event: dict) -> bool:
    """Return True if the event has integer 'timestamp' and 'value' fields."""
    return (
        isinstance(event, dict)
        and isinstance(event.get("timestamp"), int)
        and isinstance(event.get("value"), int)
    )


def _window_key(timestamp: int, window_size: int) -> int:
    """Return the floor-division bucket index for a timestamp."""
    return timestamp // window_size


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Group valid events into half-open windows of width window_size.

    Parameters
    ----------
    events:      sequence of dicts with integer 'timestamp' and 'value'.
    window_size: positive integer width of each window.

    Returns
    -------
    List of dicts sorted by window start:
        {"start": int, "count": int, "total": int}

    Raises
    ------
    ValueError if window_size is not positive.
    """
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size!r}")

    counts = defaultdict(int)
    totals = defaultdict(int)

    for event in events:
        if not _is_valid(event):
            continue
        key = _window_key(event["timestamp"], window_size)
        counts[key] += 1
        totals[key] += event["value"]

    return [
        {"start": key * window_size, "count": counts[key], "total": totals[key]}
        for key in sorted(counts)
    ]
