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


def summarize_windows(
    events: list[dict],
    window_size: int,
    *,
    include_average: bool = False,
) -> list[dict]:
    """Group valid events into half-open windows of *window_size*.

    Parameters
    ----------
    events:
        Sequence of dicts, each expected to have integer 'timestamp' and
        'value' fields.  Malformed entries are silently skipped.
    window_size:
        Positive integer width of each window.
    include_average:
        When True, each returned row includes an 'average' field equal to
        total / count.  Defaults to False.

    Returns
    -------
    list[dict]
        One row per occupied window, sorted by 'start', containing:
        {'start': int, 'count': int, 'total': int} and, when
        *include_average* is True, also {'average': float}.

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

    rows = []
    for start in sorted(counts):
        count = counts[start]
        total = totals[start]
        row: dict = {"start": start, "count": count, "total": total}
        if include_average:
            row["average"] = total / count
        rows.append(row)
    return rows
