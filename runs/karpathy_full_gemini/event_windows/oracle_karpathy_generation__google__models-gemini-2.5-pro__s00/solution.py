import collections

def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Groups events into time windows and calculates summaries for each window.

    Each event is a dictionary with integer "timestamp" and "value" fields.
    Malformed events (e.g., missing keys, non-integer values) are ignored.

    Windows are half-open intervals of the form
    [k * window_size, (k + 1) * window_size).

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of summary dictionaries, sorted by window start time. Each
        dictionary has "start", "count", and "total" keys.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    # Use a defaultdict to store aggregates: {window_start: [count, total]}
    window_aggregates = collections.defaultdict(lambda: [0, 0])

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        window_start = (timestamp // window_size) * window_size
        window_aggregates[window_start][0] += 1
        window_aggregates[window_start][1] += value

    # Convert the aggregated data into the specified list of dictionaries format.
    result = [
        {"start": start, "count": aggregates[0], "total": aggregates[1]}
        for start, aggregates in window_aggregates.items()
    ]

    # Sort the results by the window start time.
    result.sort(key=lambda item: item["start"])

    return result
