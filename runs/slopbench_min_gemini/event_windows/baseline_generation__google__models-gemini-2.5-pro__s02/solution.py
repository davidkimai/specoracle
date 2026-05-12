"""
A module for summarizing events into time-based windows.
"""

import typing

def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Groups events into time windows and calculates aggregates for each window.

    Each event is a dictionary expected to have "timestamp" and "value" integer
    fields. Malformed events (e.g., not a dict, missing keys, or values of
    the wrong type) are ignored.

    Events are grouped into half-open windows of the form
    [k * window_size, (k + 1) * window_size) based on their timestamp.

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of dictionaries, where each dictionary represents a window
        summary with "start", "count", and "total" keys. The list is sorted
        by the window start time.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    window_aggregates: typing.Dict[int, typing.Dict[str, int]] = {}

    for event in events:
        # Validate event structure and types. Ignore if malformed.
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        # Determine the start of the window for the event.
        window_start = (timestamp // window_size) * window_size

        # Aggregate count and total for the window.
        if window_start not in window_aggregates:
            window_aggregates[window_start] = {"count": 0, "total": 0}

        window_aggregates[window_start]["count"] += 1
        window_aggregates[window_start]["total"] += value

    # Format the aggregated data into the required list of dictionaries.
    result = [
        {"start": start, "count": data["count"], "total": data["total"]}
        for start, data in window_aggregates.items()
    ]

    # Sort the results by the window start time.
    result.sort(key=lambda item: item["start"])

    return result
