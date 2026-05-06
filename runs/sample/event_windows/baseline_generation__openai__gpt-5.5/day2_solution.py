def summarize_windows(
    events: list[dict], window_size: int, include_average: bool = False
) -> list[dict]:
    if (
        not isinstance(window_size, int)
        or isinstance(window_size, bool)
        or window_size <= 0
    ):
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

        if start in windows:
            windows[start][0] += 1
            windows[start][1] += value
        else:
            windows[start] = [1, value]

    rows: list[dict] = []
    for start in sorted(windows):
        count = windows[start][0]
        total = windows[start][1]
        row = {"start": start, "count": count, "total": total}
        if include_average:
            row["average"] = total / count
        rows.append(row)

    return rows
