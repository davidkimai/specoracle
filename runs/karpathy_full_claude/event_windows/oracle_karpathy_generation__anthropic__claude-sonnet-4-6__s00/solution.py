from math import floor
from collections import defaultdict


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    windows = defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        if not isinstance(event, dict):
            continue
        if "timestamp" not in event or "value" not in event:
            continue
        ts = event["timestamp"]
        val = event["value"]
        if not isinstance(ts, int) or not isinstance(val, int):
            continue
        k = ts // window_size
        start = k * window_size
        windows[start]["count"] += 1
        windows[start]["total"] += val

    result = []
    for start in sorted(windows):
        result.append({
            "start": start,
            "count": windows[start]["count"],
            "total": windows[start]["total"],
        })
    return result
