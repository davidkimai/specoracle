from typing import Any


def _is_int_field(value: Any) -> bool:
    return type(value) is int


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    if type(window_size) is not int or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    windows: dict[int, list[int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not _is_int_field(timestamp) or not _is_int_field(value):
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
