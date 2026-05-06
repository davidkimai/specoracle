from __future__ import annotations


def summarize_windows(
    events: list[dict], window_size: int, include_average: bool = False
) -> list[dict]:
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    windows: dict[int, dict[str, int]] = {}
    for event in events:
        timestamp = event.get("timestamp")
        value = event.get("value")
        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        start = (timestamp // window_size) * window_size
        summary = windows.setdefault(start, {"start": start, "count": 0, "total": 0})
        summary["count"] += 1
        summary["total"] += value

    rows = [windows[start] for start in sorted(windows)]
    if include_average:
        for row in rows:
            row["average"] = row["total"] / row["count"]

    return rows
