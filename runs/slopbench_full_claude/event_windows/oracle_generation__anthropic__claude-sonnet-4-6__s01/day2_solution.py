"""
event_windows.py

Groups events into fixed-size time windows and returns per-window summaries.
"""

from math import floor
from collections import defaultdict


def _is_valid_event(event: dict) -> bool:
    """Return True if the event has integer 'timestamp' and 'value' fields."""
    return (
        isinstance(event, dict)
        and isinstance(event.get("timestamp"), int)
        and isinstance(event.get("value"), int)
    )


def _window_start(timestamp: int, window_size: int) -> int:
    """Return the start of the window containing timestamp."""
    return (timestamp // window_size) * window_size


def summarize_windows(
    events: list[dict],
    window_size: int,
    *,
    include_average: bool = False,
) -> list[dict]:
    """
    Summarize events into non-overlapping windows of size window_size.

    Parameters
    ----------
    events : list[dict]
        Each event should have integer 'timestamp' and 'value' fields.
        Malformed events are silently ignored.
    window_size : int
        Width of each window. Must be positive.
    include_average : bool, optional
        When True, each returned row includes an "average" field equal to
        total / count. Defaults to False.

    Returns
    -------
    list[dict]
        Sorted list of {"start": int, "count": int, "total": int} dicts,
        with an additional "average" key when include_average is True.

    Raises
    ------
    ValueError
        If window_size is not positive.
    """
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size!r}")

    counts = defaultdict(int)
    totals = defaultdict(int)

    for event in events:
        if not _is_valid_event(event):
            continue
        start = _window_start(event["timestamp"], window_size)
        counts[start] += 1
        totals[start] += event["value"]

    result = []
    for start in sorted(counts):
        row = {"start": start, "count": counts[start], "total": totals[start]}
        if include_average:
            row["average"] = totals[start] / counts[start]
        result.append(row)
    return result
