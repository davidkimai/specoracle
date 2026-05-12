"""
A module for summarizing events into time-based windows.
"""

import typing


def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Groups events into fixed-size time windows and summarizes them.

    Each event is a dictionary expected to have integer "timestamp" and "value"
    fields. Events that are not dictionaries or lack these fields with the
    correct types are ignored.

    The windows are half-open intervals of the form
    [k * window_size, (k + 1) * window_size).

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of summary dictionaries, sorted by the window start time.
        Each dictionary contains "start", "count", and "total".

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    window_summaries: typing.Dict[int, typing.Dict[str, int]] = {}

    for event in events:
        # Ignore malformed events by validating structure and types.
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        # Determine the start of the window for the event using integer division.
        window_start = (timestamp // window_size) * window_size

        # Aggregate data for the window.
        if window_start not in window_summaries:
            window_summaries[window_start] = {"count": 0, "total": 0}

        summary = window_summaries[window_start]
        summary["count"] += 1
        summary["total"] += value

    # Format the aggregated data into a list of dictionaries, sorted by start time.
    result = [
        {
            "start": start,
            "count": window_summaries[start]["count"],
            "total": window_summaries[start]["total"],
        }
        for start in sorted(window_summaries)
    ]

    return result
