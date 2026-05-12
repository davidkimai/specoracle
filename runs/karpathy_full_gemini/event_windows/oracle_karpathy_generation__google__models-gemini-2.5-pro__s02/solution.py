def summarize_windows(events: list[dict], window_size: int) -> list[dict]:
    """
    Groups events into time windows and calculates aggregates for each window.

    Each event is a dictionary with "timestamp" and "value" integer fields.
    Events that are not dictionaries, are missing keys, or have non-integer
    values for these keys are ignored.

    The windows are half-open intervals of the form:
    [k * window_size, (k + 1) * window_size)

    Args:
        events: A list of event dictionaries.
        window_size: The size of each time window. Must be a positive integer.

    Returns:
        A list of summary dictionaries, sorted by the window start time.
        Each dictionary contains "start", "count", and "total".
        Returns an empty list if there are no valid events.

    Raises:
        ValueError: If window_size is not a positive integer.
    """
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer")

    window_aggregates = {}  # Maps window start time to [count, total]

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        value = event.get("value")

        if not isinstance(timestamp, int) or not isinstance(value, int):
            continue

        window_start = (timestamp // window_size) * window_size

        if window_start not in window_aggregates:
            window_aggregates[window_start] = [0, 0]

        window_aggregates[window_start][0] += 1
        window_aggregates[window_start][1] += value

    # Format the output, sorting by window start time.
    return [
        {"start": start, "count": aggregates[0], "total": aggregates[1]}
        for start, aggregates in sorted(window_aggregates.items())
    ]
