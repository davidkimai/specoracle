from __future__ import annotations


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_event(event: object) -> tuple[int, int] | None:
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
    if not _is_integer(window_size) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    if not isinstance(events, list):
        raise TypeError("events must be a list")

    totals: dict[int, dict[str, int]] = {}

    for event in events:
        parsed = _valid_event(event)
        if parsed is None:
            continue

        timestamp, value = parsed
        start = _window_start(timestamp, window_size)

        if start not in totals:
            totals[start] = {"start": start, "count": 0, "total": 0}

        totals[start]["count"] += 1
        totals[start]["total"] += value

    return [totals[start] for start in sorted(totals)]
