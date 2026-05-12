def _is_integer(value: object) -> bool:
    return type(value) is int


def _valid_event_fields(event: object) -> tuple[int, int] | None:
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

    if not isinstance(events, list):
        raise TypeError("events must be a list")

    summaries: dict[int, dict[str, int]] = {}

    for event in events:
        fields = _valid_event_fields(event)
        if fields is None:
            continue

        timestamp, value = fields
        start = (timestamp // window_size) * window_size

        if start not in summaries:
            summaries[start] = {"start": start, "count": 0, "total": 0}

        summaries[start]["count"] += 1
        summaries[start]["total"] += value

    return [summaries[start] for start in sorted(summaries)]
