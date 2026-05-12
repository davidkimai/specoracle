"""
event_windows.py

Summarize events into fixed-size time windows.
"""

from collections import defaultdict


def _is_valid_event(event: dict) -> bool:
    """Return True if event has integer 'timestamp' and 'value' fields."""
    if not isinstance(event, dict):
        return False
    timestamp = event.get("timestamp")
    value = event.get("value")
    return isinstance(timestamp, int) and isinstance(value, int)


def _validate_window_size(window_size: int) -> None:
    """Raise ValueError if window_size is not a positive integer."""
    if not isinstance(window_size, int) or isinstance(window_size, bool):
        raise ValueError(f"window_size must be a positive integer, got {window_size!r}")
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")


def _accumulate(events: list, window_size: int) -> tuple:
    """Return (counts, totals) dicts keyed by window bucket index."""
    counts = defaultdict(int)
    totals = defaultdict(int)
    for event in events:
        if not _is_valid_event(event):
            continue
        key = event["timestamp"] // window_size
        counts[key] += 1
        totals[key] += event["value"]
    return counts, totals


def _build_rows(counts: dict, totals: dict, window_size: int) -> list:
    """Convert bucket dicts into sorted list of window summary rows."""
    return [
        {"start": key * window_size, "count": counts[key], "total": totals[key]}
        for key in sorted(counts)
    ]


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Group events into half-open windows [k*window_size, (k+1)*window_size).

    Malformed events are silently ignored. Returns rows sorted by window start,
    each containing 'start', 'count', and 'total'.
    """
    _validate_window_size(window_size)
    counts, totals = _accumulate(events, window_size)
    return _build_rows(counts, totals, window_size)
