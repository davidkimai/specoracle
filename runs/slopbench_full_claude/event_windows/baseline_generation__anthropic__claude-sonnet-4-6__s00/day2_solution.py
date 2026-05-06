"""
event_windows.py

Implements summarize_windows for grouping events into fixed-size time windows.
"""

from math import floor


def summarize_windows(
    events: list[dict],
    window_size: int,
    *,
    include_average: bool = False,
) -> list[dict]:
    """
    Group events into half-open windows [k * window_size, (k + 1) * window_size).

    Parameters
    ----------
    events : list[dict]
        Each event should have integer fields "timestamp" and "value".
        Malformed events (missing fields, non-integer values) are ignored.
    window_size : int
        The size of each window. Must be a positive integer.
    include_average : bool, optional
        When True, each returned row includes an "average" field equal to
        total / count. Defaults to False.

    Returns
    -------
    list[dict]
        Sorted list of dicts with keys "start", "count", and "total".
        If include_average is True, each dict also contains "average".

    Raises
    ------
    ValueError
        If window_size is not positive.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")

    windows: dict[int, dict] = {}

    for event in events:
        # Validate event is a dict with integer "timestamp" and "value"
        if not isinstance(event, dict):
            continue
        timestamp = event.get("timestamp")
        value = event.get("value")
        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue
        # Booleans are subclasses of int in Python; treat them as malformed
        if isinstance(timestamp, bool) or isinstance(value, bool):
            continue

        k = floor(timestamp / window_size)
        start = k * window_size

        if start not in windows:
            windows[start] = {"start": start, "count": 0, "total": 0}
        windows[start]["count"] += 1
        windows[start]["total"] += value

    result = [windows[start] for start in sorted(windows)]

    if include_average:
        for row in result:
            row["average"] = row["total"] / row["count"]

    return result
