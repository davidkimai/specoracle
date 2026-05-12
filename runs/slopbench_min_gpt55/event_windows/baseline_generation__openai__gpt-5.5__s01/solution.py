from typing import Any


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Group well-formed events into half-open time windows.

    A well-formed event is a dict containing integer "timestamp" and "value"
    fields. Malformed events are ignored.

    Windows are [k * window_size, (k + 1) * window_size), where k is computed
    using integer floor division.
    """
    if type(window_size) is not int or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    windows: dict[int, dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp: Any = event.get("timestamp")
        value: Any = event.get("value")

        if type(timestamp) is not int or type(value) is not int:
            continue

        start = (timestamp // window_size) * window_size

        if start not in windows:
            windows[start] = {"start": start, "count": 0, "total": 0}

        windows[start]["count"] += 1
        windows[start]["total"] += value

    return [windows[start] for start in sorted(windows)]


__all__ = ["summarize_windows"]
