from typing import Any


def _is_int_field(value: Any) -> bool:
    """Return True for integer fields, excluding booleans."""
    return isinstance(value, int) and not isinstance(value, bool)


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Group well-formed events into half-open integer windows.

    Each well-formed event is a dictionary with integer "timestamp" and "value"
    fields. Malformed events are ignored.

    Args:
        events: A list of event dictionaries.
        window_size: Positive integer size of each window.

    Returns:
        A list of dictionaries sorted by window start, each containing:
        {"start": start, "count": count, "total": total}

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not _is_int_field(window_size) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    windows: dict[int, dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not _is_int_field(timestamp) or not _is_int_field(value):
            continue

        start = (timestamp // window_size) * window_size

        if start not in windows:
            windows[start] = {"start": start, "count": 0, "total": 0}

        windows[start]["count"] += 1
        windows[start]["total"] += value

    return [windows[start] for start in sorted(windows)]
