"""
event_windows.py – group timestamped events into fixed-size windows.
"""

from __future__ import annotations

import math
from collections import defaultdict


def _is_valid(event: dict) -> bool:
    """Return True only when the event has integer 'timestamp' and 'value'."""
    if not isinstance(event, dict):
        return False
    ts = event.get("timestamp")
    val = event.get("value")
    return isinstance(ts, int) and isinstance(val, int)


def _window_key(timestamp: int, window_size: int) -> int:
    """Return the window start for a given timestamp."""
    return math.floor(timestamp / window_size) * window_size


def summarize_windows(
    events: list[dict],
    window_size: int,
    *,
    include_average: bool = False,
) -> list[dict]:
    """
    Summarise *events* into non-overlapping windows of *window_size*.

    Parameters
    ----------
    events:
        Sequence of dicts, each expected to contain integer 'timestamp'
        and 'value' fields.  Malformed entries are silently ignored.
    window_size:
        Positive integer width of each window.
    include_average:
        When True, each returned row includes an "average" field equal to
        total / count (float).  Defaults to False.

    Returns
    -------
    List of dicts sorted by window start::

        {"start": <int>, "count": <int>, "total": <int>}

    When *include_average* is True::

        {"start": <int>, "count": <int>, "total": <int>, "average": <float>}
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)

    for event in events:
        if not _is_valid(event):
            continue
        key = _window_key(event["timestamp"], window_size)
        counts[key] += 1
        totals[key] += event["value"]

    result = []
    for start in sorted(counts):
        row: dict = {
            "start": start,
            "count": counts[start],
            "total": totals[start],
        }
        if include_average:
            row["average"] = totals[start] / counts[start]
        result.append(row)

    return result
