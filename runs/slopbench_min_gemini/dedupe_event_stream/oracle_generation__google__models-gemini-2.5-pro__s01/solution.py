"""
Deduplicates events from a stream based on a composite key and a time window.

This module provides a function to filter a list of event dictionaries,
retaining only the first event for a given composite key within a specified
rolling time window.
"""

from typing import Any, Dict, List, Optional, Tuple


def _get_composite_key(
    event: Dict[str, Any], key_fields: List[str]
) -> Optional[Tuple]:
    """
    Extracts a composite key from an event dictionary.

    Args:
        event: The event dictionary.
        key_fields: A list of keys that form the composite key.

    Returns:
        A tuple of the values corresponding to the key_fields, or None if
        any key is missing from the event.
    """
    try:
        # A tuple is used because it is hashable and can serve as a dictionary key.
        return tuple(event[k] for k in key_fields)
    except KeyError:
        return None


def _parse_event_data(
    event: Dict[str, Any], key_fields: List[str]
) -> Optional[Tuple[Tuple, int]]:
    """
    Validates an event and extracts its composite key and timestamp.

    Args:
        event: The event dictionary to parse.
        key_fields: The list of keys for the composite key.

    Returns:
        A tuple containing (composite_key, timestamp) if the event is valid,
        otherwise None. An event is considered valid if it is a dictionary
        containing an integer 'timestamp' and all specified key_fields.
    """
    if not isinstance(event, dict):
        return None

    timestamp = event.get('timestamp')
    if not isinstance(timestamp, int):
        return None

    composite_key = _get_composite_key(event, key_fields)
    if composite_key is None:
        return None

    return composite_key, timestamp


def dedupe_events(
    events: List[Dict[str, Any]],
    key_fields: List[str],
    window_seconds: int
) -> List[Dict[str, Any]]:
    """
    Keeps the first event for each composite key within a rolling time window.

    A duplicate is any event with the same composite key that occurs within
    `window_seconds` of a previously kept event for that same key. The order
    of the retained events from the original stream is preserved.

    Malformed events are skipped. An event is considered malformed if it is not
    a dictionary, is missing the 'timestamp' key, has a non-integer timestamp,
    or is missing any of the specified `key_fields`.

    Args:
        events: A list of event dictionaries.
        key_fields: A list of dictionary keys that form the composite key
                    for deduplication.
        window_seconds: The duration of the deduplication window in seconds.
                        Must be a non-negative integer.

    Returns:
        A new list of event dictionaries with duplicates removed.

    Raises:
        TypeError: If `events` is not a list, or `key_fields` is not a list
                   of strings.
        ValueError: If `window_seconds` is not a non-negative integer.
    """
    if not isinstance(events, list):
        raise TypeError("Input 'events' must be a list of dictionaries.")
    if not isinstance(key_fields, list) or not all(
        isinstance(k, str) for k in key_fields
    ):
        raise TypeError("Input 'key_fields' must be a list of strings.")
    if not isinstance(window_seconds, int) or window_seconds < 0:
        raise ValueError("Input 'window_seconds' must be a non-negative integer.")

    last_kept_timestamps: Dict[Tuple, int] = {}
    retained_events: List[Dict[str, Any]] = []

    for event in events:
        parsed_data = _parse_event_data(event, key_fields)
        if parsed_data is None:
            continue

        composite_key, current_timestamp = parsed_data
        last_kept_timestamp = last_kept_timestamps.get(composite_key)

        if last_kept_timestamp is None:
            # This is the first time this composite key has been seen.
            retained_events.append(event)
            last_kept_timestamps[composite_key] = current_timestamp
            continue

        time_since_last_kept = current_timestamp - last_kept_timestamp
        if time_since_last_kept >= window_seconds:
            # The window has expired, so this event is not a duplicate.
            retained_events.append(event)
            last_kept_timestamps[composite_key] = current_timestamp
        # Otherwise, the event is within the window and is a duplicate; skip it.

    return retained_events
