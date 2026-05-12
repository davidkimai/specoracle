from collections import defaultdict
import math


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    buckets = defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        if not isinstance(event, dict):
            continue
        if "timestamp" not in event or "value" not in event:
            continue
        ts = event["timestamp"]
        val = event["value"]
        if not isinstance(ts, int) or not isinstance(val, int):
            continue
        k = math.floor(ts / window_size)
        buckets[k]["count"] += 1
        buckets[k]["total"] += val

    result = []
    for k in sorted(buckets):
        start = k * window_size
        result.append({"start": start, "count": buckets[k]["count"], "total": buckets[k]["total"]})

    return result
