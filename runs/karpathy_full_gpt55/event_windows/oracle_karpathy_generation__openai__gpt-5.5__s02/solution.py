"""Summarize timestamped integer events into fixed-size half-open windows."""

from typing import Any


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """Return per-window counts and totals for well-formed events.

    Well-formed events are dictionaries with integer "timestamp" and "value"
    fields. Other events are ignored. Windows are half-open intervals of size
    window_size, aligned at multiples of window_size.
    """
    if type(window_size) is not int or window_size <= 0:
        raise ValueError("window_size must be positive")

    windows: dict[int, list[int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp: Any = event.get("timestamp")
        value: Any = event.get("value")
        if type(timestamp) is not int or type(value) is not int:
            continue

        start = (timestamp // window_size) * window_size
        if start not in windows:
            windows[start] = [0, 0]
        windows[start][0] += 1
        windows[start][1] += value

    return [
        {"start": start, "count": windows[start][0], "total": windows[start][1]}
        for start in sorted(windows)
    ]
