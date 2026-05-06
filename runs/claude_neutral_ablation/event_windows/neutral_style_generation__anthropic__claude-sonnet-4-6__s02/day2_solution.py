from collections import defaultdict


def summarize_windows(events: list[dict], window_size: int, *, include_average: bool = False) -> list[dict]:
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    buckets = defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        if not isinstance(event, dict):
            continue
        timestamp = event.get("timestamp")
        value = event.get("value")
        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue
        k = timestamp // window_size
        start = k * window_size
        buckets[start]["count"] += 1
        buckets[start]["total"] += value

    result = []
    for start in sorted(buckets.keys()):
        b = buckets[start]
        row = {"start": start, "count": b["count"], "total": b["total"]}
        if include_average:
            row["average"] = b["total"] / b["count"]
        result.append(row)

    return result
