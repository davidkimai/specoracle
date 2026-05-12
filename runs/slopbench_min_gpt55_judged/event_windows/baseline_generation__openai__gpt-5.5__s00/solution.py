def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """Summarize integer-valued events into half-open time windows.

    Events must be dictionaries containing integer "timestamp" and "value" fields.
    Malformed events are ignored.

    Args:
        events: A list of event dictionaries.
        window_size: Positive integer window size.

    Returns:
        A list of dictionaries sorted by window start, each with:
        {"start": start, "count": count, "total": total}

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or isinstance(window_size, bool) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    windows: dict[int, list[int]] = {}

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

        if start not in windows:
            windows[start] = [0, 0]

        windows[start][0] += 1
        windows[start][1] += value

    return [
        {"start": start, "count": windows[start][0], "total": windows[start][1]}
        for start in sorted(windows)
    ]
