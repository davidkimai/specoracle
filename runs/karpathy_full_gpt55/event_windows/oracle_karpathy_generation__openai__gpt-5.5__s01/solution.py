def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    if not isinstance(window_size, int) or isinstance(window_size, bool) or window_size <= 0:
        raise ValueError("window_size must be positive")

    windows = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if (
            not isinstance(timestamp, int)
            or isinstance(timestamp, bool)
            or not isinstance(value, int)
            or isinstance(value, bool)
        ):
            continue

        start = (timestamp // window_size) * window_size
        count, total = windows.get(start, (0, 0))
        windows[start] = (count + 1, total + value)

    return [
        {"start": start, "count": count, "total": total}
        for start, (count, total) in sorted(windows.items())
    ]
