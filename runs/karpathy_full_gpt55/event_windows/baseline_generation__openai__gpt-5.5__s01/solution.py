"""Utilities for summarizing timestamped events into fixed-size windows."""

from typing import Any


def _is_integer(value: Any) -> bool:
    """Return True for integers, excluding booleans."""
    return isinstance(value, int) and not isinstance(value, bool)


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Summarize well-formed events into half-open integer windows.

    Each well-formed event is a dict containing integer "timestamp" and "value"
    fields. Malformed events are ignored.

    Windows are:
        [k * window_size, (k + 1) * window_size)

    Args:
        events: A list of event dictionaries.
        window_size: Positive integer window size.

    Returns:
        A list of dictionaries sorted by window start:
        {"start": start, "count": count, "total": total}

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not _is_integer(window_size) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    windows: dict[int, list[int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not _is_integer(timestamp) or not _is_integer(value):
            continue

        start = (timestamp // window_size) * window_size

        if start not in windows:
            windows[start] = [0, 0]

        windows[start][0] += 1
        windows[start][1] += value

    return [
        {"start": start, "count": count_total[0], "total": count_total[1]}
        for start, count_total in sorted(windows.items())
    ]
