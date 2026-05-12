"""
A module for deduplicating events in a stream based on a composite key
and a rolling time window.
"""

from typing import Any, Dict, Hashable, List, Tuple


def dedupe_events(
    events: List[Dict[str, Any]],
    key_fields: List[str],
    window_seconds: int,
) -> List[Dict[str, Any]]:
    """Keeps the first event for each composite key within a rolling window.

    This function processes a list of event dictionaries, identifies duplicates
    based on a composite key and a time window, and returns a new list
    containing only the unique events in their original order.

    An event is considered a duplicate if it has the same composite key as a
    previously kept event and its timestamp falls within `window_seconds` of
    that event's timestamp.

    Malformed events are skipped. An event is malformed if:
    - It lacks the 'timestamp' key or the value is not an integer.
    - It lacks any of the keys specified in `key_fields`.
    - The values for the `key_fields` form a non-hashable composite key.

    Args:
        events: A list of event dictionaries. Each dictionary must contain an
            integer 'timestamp' field and all fields listed in `key_fields`.
        key_fields: A list of dictionary keys that together form the composite
            key for deduplication.
        window_seconds: The duration of the deduplication window in seconds.
            An event is a duplicate if its timestamp is less than
            `window_seconds` after a kept event with the same key.

    Returns:
        A new list of event dictionaries with duplicates removed, preserving
        the relative order of the kept events.
    """
    last_kept_timestamps: Dict[Tuple[Hashable, ...], int] = {}
    deduplicated_events: List[Dict[str, Any]] = []

    for event in events:
        # Validate that the event has an integer 'timestamp' field.
        timestamp = event.get('timestamp')
        if not isinstance(timestamp, int):
            continue

        # Validate that all key fields are present.
        if not all(key in event for key in key_fields):
            continue

        # Construct the composite key from the specified fields.
        try:
            composite_key = tuple(event[key] for key in key_fields)
        except TypeError:
            # This occurs if a value for a key_field is not hashable (e.g., a list).
            # Treat such events as malformed and skip them.
            continue

        last_kept_ts = last_kept_timestamps.get(composite_key)

        if last_kept_ts is None:
            # This is the first time we've seen this composite key. Keep the event.
            deduplicated_events.append(event)
            last_kept_timestamps[composite_key] = timestamp
        else:
            # A previous event with this key was kept. Check if the current
            # event is outside the deduplication window.
            if timestamp >= last_kept_ts + window_seconds:
                # The window has passed. Keep this event and reset the window start.
                deduplicated_events.append(event)
                last_kept_timestamps[composite_key] = timestamp
            # Otherwise, the event is within the window and is a duplicate. Skip it.

    return deduplicated_events
