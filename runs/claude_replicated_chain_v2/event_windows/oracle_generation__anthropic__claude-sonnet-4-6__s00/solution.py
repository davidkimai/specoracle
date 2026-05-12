"""
event_windows.py

Summarise events into fixed-size time windows.
"""

from __future__ import annotations

import math
from collections import defaultdict


def _is_valid_event(event: object) -> bool:
    """Return True when *event* has integer 'timestamp' and 'value' fields."""
    if not isinstance(event, dict):
        return False
    return (
        isinstance(event.get("timestamp"), int)
        and isinstance(event.get("value"), int)
    )


def _window_start(timestamp: int, window_size: int) -> int:
    """Return the start of the window that contains *timestamp*."""
    return math.floor(timestamp / window_size) * window_size


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """Group valid events into half-open windows of *window_size*.

    Parameters
    ----------
    events:
        Sequence of dicts, each expected to have integer 'timestamp' and
        'value' fields.  Malformed entries are silently skipped.
    window_size:
        Positive integer width of each window.

    Returns
    -------
    list[dict]
        One row per occupied window, sorted by 'start', containing:
        {'start': int, 'count': int, 'total': int}.

    Raises
    ------
    ValueError
        If *window_size* is not a positive integer.
    """
    if not isinstance(window_size, int) or isinstance(window_size, bool):
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")

    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not _is_valid_event(event):
            continue
        start = _window_start(event["timestamp"], window_size)
        counts[start] += 1
        totals[start] += event["value"]

    return [
        {"start": start, "count": counts[start], "total": totals[start]}
        for start in sorted(counts)
    ]
