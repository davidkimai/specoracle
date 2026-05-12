"""
Deduplicates events in a stream based on a composite key and a time window.
"""

from typing import Any, Dict, List, Tuple


def _is_valid_event(event: Dict[str, Any], key_fields: List[str]) -> bool:
    """
    Checks if an event dictionary is well-formed for deduplication.

    An event is valid if it's a dictionary containing an integer 'timestamp'
    and all specified key_fields.
    """
    if not isinstance(event, dict):
        return False

    if 'timestamp' not in event or not isinstance(event.get('timestamp'), int):
        return False

    for key in key_fields:
        if key not in event:
            return False

    return True


def _extract_composite_key(event: Dict[str, Any], key_fields: List[str]) -> Tuple:
    """
    Extracts a composite key from a valid event.

    The key is a tuple of the values corresponding to the key_fields,
    which makes it hashable for use in dictionaries.
    """
    return tuple(event[key] for key in key_fields)


def dedupe_events(
    events: List[Dict[str, Any]],
    key_fields: List[str],
    window_seconds: int
) -> List[Dict[str, Any]]:
    """
    Keeps the first event for each composite key within a rolling time window.

    This function iterates through a list of events, preserving the first
    occurrence of an event based on a composite key. Subsequent events with the
    same composite key are considered duplicates and discarded if their
    timestamp falls within `window_seconds` of the last kept event's timestamp
    for that key.

    Args:
        events: A list of dictionaries, where each dictionary represents an
                event. Events must be processed in their original order.
        key_fields: A list of strings representing the dictionary keys that
                    form the composite key for deduplication.
        window_seconds: An integer defining the duration of the deduplication
                        window.

    Returns:
        A new list of event dictionaries with duplicates removed, preserving
        the original order of the retained events.

    Raises:
        TypeError: If `events` is not a list, `key_fields` is not a list of
                   strings, or `window_seconds` is not an integer.
        ValueError: If `window_seconds` is negative.
    """
    if not isinstance(events, list):
        raise TypeError("Input 'events' must be a list of dictionaries.")
    if not isinstance(key_fields, list) or not all(isinstance(k, str) for k in key_fields):
        raise TypeError("Input 'key_fields' must be a list of strings.")
    if not isinstance(window_seconds, int):
        raise TypeError("Input 'window_seconds' must be an integer.")
    if window_seconds < 0:
        raise ValueError("Input 'window_seconds' must be a non-negative integer.")

    retained_events: List[Dict[str, Any]] = []
    last_kept_timestamps: Dict[Tuple, int] = {}

    for event in events:
        if not _is_valid_event(event, key_fields):
            continue

        composite_key = _extract_composite_key(event, key_fields)
        current_timestamp = event['timestamp']

        last_kept_timestamp = last_kept_timestamps.get(composite_key)

        if last_kept_timestamp is None:
            # First time seeing this composite key. Keep the event.
            retained_events.append(event)
            last_kept_timestamps[composite_key] = current_timestamp
        else:
            # Key has been seen. Check if the current event is outside the window.
            if current_timestamp >= last_kept_timestamp + window_seconds:
                retained_events.append(event)
                last_kept_timestamps[composite_key] = current_timestamp

    return retained_events
