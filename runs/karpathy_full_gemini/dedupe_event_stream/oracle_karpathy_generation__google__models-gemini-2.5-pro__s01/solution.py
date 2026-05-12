"""
This module provides functionality to deduplicate event streams.
"""

import typing


def dedupe_events(
    events: list[dict], key_fields: list[str], window_seconds: int
) -> list[dict]:
    """
    Keeps the first event for each composite key within a rolling timestamp window.

    This function processes a list of event dictionaries, identifies duplicates
    based on a composite key and a time window, and returns a new list
    containing only the unique events in their original order.

    An event is considered a duplicate if it has the same composite key as a
    previously kept event and its timestamp falls within `window_seconds` of
    that kept event's timestamp.

    Malformed events (e.g., missing 'timestamp' or a key field) are skipped.

    Args:
        events: A list of dictionaries, where each dictionary represents an
            event. Each event must contain an integer 'timestamp' field.
        key_fields: A list of strings representing the dictionary keys that
            form the composite key for deduplication.
        window_seconds: An integer representing the time window in seconds.
            A subsequent event is a duplicate if its timestamp is less than
            the kept event's timestamp plus this window.

    Returns:
        A list of deduplicated event dictionaries, preserving the original
        order of the retained events.
    """
    last_seen_timestamps: dict[tuple, int] = {}
    deduplicated_events: list[dict] = []

    for event in events:
        # Validate that the event contains an integer timestamp.
        if "timestamp" not in event or not isinstance(event.get("timestamp"), int):
            continue

        # Construct the composite key for the event.
        try:
            composite_key = tuple(event[key] for key in key_fields)
        except KeyError:
            # Skip event if any part of the composite key is missing.
            continue

        current_timestamp = event["timestamp"]

        # Check if the event is a duplicate within the time window.
        if composite_key in last_seen_timestamps:
            kept_event_timestamp = last_seen_timestamps[composite_key]
            if current_timestamp < kept_event_timestamp + window_seconds:
                # Event is within the window of a previously kept event, so it's a duplicate.
                continue

        # This event is not a duplicate; keep it and update the window for its key.
        deduplicated_events.append(event)
        last_seen_timestamps[composite_key] = current_timestamp

    return deduplicated_events
