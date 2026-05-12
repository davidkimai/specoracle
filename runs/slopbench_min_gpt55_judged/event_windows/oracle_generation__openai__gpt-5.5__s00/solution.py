from typing import Any

__all__ = ["summarize_windows"]


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_window_size(window_size: int) -> None:
    if not _is_integer(window_size) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")


def _event_numbers(event: Any) -> tuple[int, int] | None:
    if not isinstance(event, dict):
        return None

    timestamp = event.get("timestamp")
    value = event.get("value")

    if not _is_integer(timestamp) or not _is_integer(value):
        return None

    return timestamp, value


def _window_start(timestamp: int, window_size: int) -> int:
    return (timestamp // window_size) * window_size


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    _validate_window_size(window_size)

    windows: dict[int, tuple[int, int]] = {}

    for event in events:
        numbers = _event_numbers(event)
        if numbers is None:
            continue

        timestamp, value = numbers
        start = _window_start(timestamp, window_size)
        count, total = windows.get(start, (0, 0))
        windows[start] = (count + 1, total + value)

    return [
        {"start": start, "count": count, "total": total}
        for start, (count, total) in sorted(windows.items())
    ]
