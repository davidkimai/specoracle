import collections
from typing import Dict, List, Optional, Tuple


def _parse_valid_event(event: Dict) -> Optional[Tuple[int, int]]:
    """
    Parses an event dictionary, returning (timestamp, value) if valid.

    A valid event is a dictionary with integer "timestamp" and "value" fields.
    Returns None if the event is malformed.
    """
    if not isinstance(event, dict):
        return None

    timestamp = event.get("timestamp")
    value = event.get("value")

    if not isinstance(timestamp, int) or not isinstance(value, int):
        return None

    return timestamp, value


def _get_window_start(timestamp: int, window_size: int) -> int:
    """Calculates the start of the window for a given timestamp."""
    # Integer floor division correctly assigns the timestamp to a window.
    # For example, with window_size=10, timestamps 0-9 fall into window 0,
    # 10-19 into window 10, etc.
    return (timestamp // window_size) * window_size


def summarize_windows(events: List[Dict], window_size: int) -> List[Dict]:
    """
    Groups events into time windows and calculates summaries for each window.

    Args:
        events: A list of event dictionaries, each expected to have "timestamp"
                and "value" integer fields. Malformed events are ignored.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of summary dictionaries, sorted by window start time. Each
        summary includes the window "start", the "count" of events, and the
        "total" of their values.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    # The factory creates a new summary dict for each new window start.
    window_summaries = collections.defaultdict(lambda: {"count": 0, "total": 0})

    for event in events:
        parsed_event = _parse_valid_event(event)
        if parsed_event is None:
            continue

        timestamp, value = parsed_event
        start = _get_window_start(timestamp, window_size)

        summary = window_summaries[start]
        summary["count"] += 1
        summary["total"] += value

    # Convert the aggregated data into the required list format.
    result = [
        {"start": start, "count": summary["count"], "total": summary["total"]}
        for start, summary in window_summaries.items()
    ]

    # Sort the results by the window start time for a predictable output.
    result.sort(key=lambda item: item["start"])

    return result
