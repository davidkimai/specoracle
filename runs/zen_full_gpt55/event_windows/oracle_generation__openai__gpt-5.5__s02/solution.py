def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _event_fields(event: object) -> tuple[int, int] | None:
    if not isinstance(event, dict):
        return None

    timestamp = event.get("timestamp")
    value = event.get("value")

    if not _is_integer(timestamp) or not _is_integer(value):
        return None

    return timestamp, value


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    if not _is_integer(window_size) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    totals_by_start: dict[int, tuple[int, int]] = {}

    for event in events:
        fields = _event_fields(event)
        if fields is None:
            continue

        timestamp, value = fields
        start = (timestamp // window_size) * window_size

        count, total = totals_by_start.get(start, (0, 0))
        totals_by_start[start] = count + 1, total + value

    return [
        {"start": start, "count": count, "total": total}
        for start, (count, total) in sorted(totals_by_start.items())
    ]
