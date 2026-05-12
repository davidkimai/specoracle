"""A module for summarizing time-series events into windows."""

from typing import List, Dict, Any


def summarize_windows(
    events: List[Dict[str, Any]], window_size: int
) -> List[Dict[str, int]]:
    """Groups events into fixed-size time windows and calculates summaries.

    Each event is a dictionary expected to have "timestamp" and "value" integer
    fields. Malformed events (e.g., not a dict, missing keys, or values of
    the wrong type) are ignored.

    The windows are half-open intervals of the form
    [k * window_size, (k + 1) * window_size).

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of dictionaries, each representing a summarized window,
        sorted by the window start time. Each dictionary contains:
        - "start": The start timestamp of the window.
        - "count": The number of events in the window.
        - "total": The sum of event values in the window.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    # A dictionary to hold summaries, mapping window_start to {"count", "total"}
    window_summaries: Dict[int, Dict[str, int]] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        # Determine the start of the window for the current event
        window_start = (timestamp // window_size) * window_size

        # Get or create the summary for this window
        summary = window_summaries.setdefault(
            window_start, {"count": 0, "total": 0}
        )

        # Update the summary
        summary["count"] += 1
        summary["total"] += value

    # Create the final list of summaries, sorted by window start time
    sorted_starts = sorted(window_summaries.keys())

    result = [
        {
            "start": start,
            "count": window_summaries[start]["count"],
            "total": window_summaries[start]["total"],
        }
        for start in sorted_starts
    ]

    return result
