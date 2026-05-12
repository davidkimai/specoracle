from typing import Optional, Tuple

__all__ = ["summarize_windows"]

_MISSING = object()


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_window_size(window_size: int) -> None:
    if not _is_integer(window_size) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")


def _extract_event(event: object) -> Optional[Tuple[int, int]]:
    if not isinstance(event, dict):
        return None

    timestamp = event.get("timestamp", _MISSING)
    value = event.get("value", _MISSING)

    if not _is_integer(timestamp) or not _is_integer(value):
        return None

    return timestamp, value


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    _validate_window_size(window_size)

    windows: dict[int, list[int]] = {}

    for event in events:
        extracted = _extract_event(event)
        if extracted is None:
            continue

        timestamp, value = extracted
        start = (timestamp // window_size) * window_size

        if start not in windows:
            windows[start] = [0, 0]

        windows[start][0] += 1
        windows[start][1] += value

    return [
        {"start": start, "count": count_total[0], "total": count_total[1]}
        for start, count_total in sorted(windows.items())
    ]
