from __future__ import annotations


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    if not _is_plain_integer(window_size) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    windows: dict[int, tuple[int, int]] = {}

    for event in events:
        if not _is_valid_event(event):
            continue

        timestamp = event["timestamp"]
        value = event["value"]
        start = (timestamp // window_size) * window_size

        count, total = windows.get(start, (0, 0))
        windows[start] = (count + 1, total + value)

    return [
        {"start": start, "count": count, "total": total}
        for start, (count, total) in sorted(windows.items())
    ]


def _is_valid_event(event: object) -> bool:
    if not isinstance(event, dict):
        return False

    if "timestamp" not in event or "value" not in event:
        return False

    return _is_plain_integer(event["timestamp"]) and _is_plain_integer(event["value"])


def _is_plain_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
