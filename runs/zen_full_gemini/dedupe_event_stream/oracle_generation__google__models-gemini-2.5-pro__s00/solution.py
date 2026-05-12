"""
A module for deduplicating events from a stream based on a composite key
and a rolling time window.
"""

import typing


def _validate_and_extract_key(
    event: typing.Dict[str, typing.Any], key_fields: typing.List[str]
) -> typing.Optional[typing.Tuple[tuple, int]]:
    """
    Validates an event and extracts its composite key and timestamp.

    An event is considered valid if it is a dictionary containing an integer
    'timestamp' key and all fields specified in `key_fields`. The values for
    the key fields must be hashable.

    Args:
        event: The event dictionary to process.
        key_fields: A list of strings representing the fields that form the
                    composite key.

    Returns:
        A tuple of (composite_key, timestamp) if the event is valid,
        otherwise None. The composite_key is a tuple of the values from
        the key_fields.
    """
    if not isinstance(event, dict):
        return None

    timestamp = event.get("timestamp")
    if not isinstance(timestamp, int):
        return None

    try:
        key_values = tuple(event[field] for field in key_fields)
    except KeyError:
        # A required key field was missing in the event.
        return None
    except TypeError:
        # A value for a key field was not hashable (e.g., a list).
        return None

    return key_values, timestamp


def dedupe_events(
    events: typing.List[typing.Dict[str, typing.Any]],
    key_fields: typing.List[str],
    window_seconds: int,
) -> typing.List[typing.Dict[str, typing.Any]]:
    """
    Keeps the first event for each composite key within a rolling time window.

    This function processes a list of event dictionaries, preserving the first
    occurrence of an event based on a composite key within a specified time
    window. Subsequent events with the same key are considered duplicates and
    are discarded if their timestamp falls within `window_seconds` of the
    last kept event for that key.

    - Events must be dictionaries.
    - Each event must contain an integer 'timestamp' field.
    - Each event must contain all fields listed in `key_fields`.
    - Malformed events that do not meet these criteria are silently skipped.
    - The relative order of the retained events is preserved.

    Args:
        events: A list of event dictionaries to be deduplicated.
        key_fields: A list of dictionary keys that together form the unique
                    identifier for an event type.
        window_seconds: The duration in seconds of the deduplication window.
                        An event is a duplicate if its timestamp is less than
                        the kept event's timestamp plus this window.

    Returns:
        A new list of event dictionaries with duplicates removed.

    Raises:
        TypeError: If `events` is not a list, `key_fields` is not a list
                   of strings, or one of its elements is not a string.
        ValueError: If `window_seconds` is a negative integer.
    """
    if not isinstance(events, list):
        raise TypeError("`events` must be a list of dictionaries.")
    if not isinstance(key_fields, list) or not all(
        isinstance(k, str) for k in key_fields
    ):
        raise TypeError("`key_fields` must be a list of strings.")
    if not isinstance(window_seconds, int) or window_seconds < 0:
        raise ValueError("`window_seconds` must be a non-negative integer.")

    # Stores the timestamp of the last kept event for each composite key.
    # {composite_key: last_kept_timestamp}
    last_seen_timestamps: typing.Dict[tuple, int] = {}
    kept_events: typing.List[typing.Dict[str, typing.Any]] = []

    for event in events:
        parsed_data = _validate_and_extract_key(event, key_fields)
        if parsed_data is None:
            continue

        composite_key, timestamp = parsed_data
        last_kept_timestamp = last_seen_timestamps.get(composite_key)

        if last_kept_timestamp is not None:
            is_duplicate = timestamp < last_kept_timestamp + window_seconds
            if is_duplicate:
                continue

        # Keep the event if it's the first for this key or outside the window.
        kept_events.append(event)
        last_seen_timestamps[composite_key] = timestamp

    return kept_events
