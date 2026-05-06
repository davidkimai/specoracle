"""
event_windows: group timestamped events into fixed-size windows.
"""

from collections import defaultdict


def _is_valid(event: dict) -> bool:
    """Return True if the event has integer 'timestamp' and 'value' fields."""
    return (
        isinstance(event, dict)
        and isinstance(event.get("timestamp"), int)
        and isinstance(event.get("value"), int)
    )


def _window_key(timestamp: int, window_size: int) -> int:
    """Return the floor-division bucket index for a timestamp."""
    return timestamp // window_size


def summarize_windows(
    events: list[dict],
    window_size: int,
    *,
    include_average: bool = False,
) -> list[dict]:
    """
    Group valid events into half-open windows of width window_size.

    Parameters
    ----------
    events:          sequence of dicts with integer 'timestamp' and 'value'.
    window_size:     positive integer width of each window.
    include_average: when True, each row includes "average" = total / count.

    Returns
    -------
    List of dicts sorted by window start:
        {"start": int, "count": int, "total": int}
    or, when include_average is True:
        {"start": int, "count": int, "total": int, "average": float}

    Raises
    ------
    ValueError if window_size is not positive.
    """
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size!r}")

    counts = defaultdict(int)
    totals = defaultdict(int)

    for event in events:
        if not _is_valid(event):
            continue
        key = _window_key(event["timestamp"], window_size)
        counts[key] += 1
        totals[key] += event["value"]

    result = []
    for key in sorted(counts):
        count = counts[key]
        total = totals[key]
        row = {"start": key * window_size, "count": count, "total": total}
        if include_average:
            row["average"] = total / count
        result.append(row)

    return result
