"""
A module for deduplicating a stream of events based on a composite key
and a rolling time window.
"""
import typing

# Type alias for clarity.
Event = typing.Dict[str, typing.Any]


def _validate_dedupe_inputs(
    events: typing.List[Event],
    key_fields: typing.List[str],
    window_seconds: int,
) -> None:
    """
    Validates the main inputs for the deduplication function.

    Raises:
        TypeError: If inputs are not of the expected container types.
        ValueError: If `key_fields` is empty or `window_seconds` is invalid.
    """
    if not isinstance(events, list):
        raise TypeError("`events` must be a list of dictionaries.")

    if not isinstance(key_fields, list) or not all(
        isinstance(k, str) for k in key_fields
    ):
        raise TypeError("`key_fields` must be a list of strings.")

    if not key_fields:
        raise ValueError("`key_fields` must not be empty.")

    if not isinstance(window_seconds, int) or window_seconds < 0:
        raise ValueError("`window_seconds` must be a non-negative integer.")


def _is_event_well_formed(event: typing.Any, key_fields: list[str]) -> bool:
    """
    Checks if an event has the required structure and types.

    An event is well-formed if it is a dictionary containing an integer
    'timestamp' field and all specified `key_fields`.
    """
    if not isinstance(event, dict):
        return False

    if "timestamp" not in event or not isinstance(event.get("timestamp"), int):
        return False

    return all(key in event for key in key_fields)


def dedupe_events(
    events: typing.List[Event],
    key_fields: typing.List[str],
    window_seconds: int,
) -> typing.List[Event]:
    """
    Deduplicates a list of events based on a composite key and time window.

    This function keeps the first event for each composite key within a rolling
    timestamp window. A duplicate is any later event with the same composite
    key and a timestamp less than `window_seconds` after the kept event's
    timestamp. Malformed events (e.g., missing 'timestamp' or key fields) are
    skipped. The order of the retained events is preserved from the original
    list.

    Args:
        events: A list of event dictionaries.
        key_fields: A list of dictionary keys to form the composite key for
                    deduplication.
        window_seconds: The duration of the deduplication window in seconds.

    Returns:
        A new list of events with duplicates removed.

    Raises:
        ValueError: If `key_fields` is empty or `window_seconds` is negative.
        TypeError: If `events` or `key_fields` have an incorrect type, or if
                   a value for a key field is not hashable.
    """
    _validate_dedupe_inputs(events, key_fields, window_seconds)

    kept_events: typing.List[Event] = []
    last_seen_timestamps: typing.Dict[tuple, int] = {}

    for event in events:
        if not _is_event_well_formed(event, key_fields):
            continue

        composite_key = tuple(event[key] for key in key_fields)
        current_timestamp = event["timestamp"]

        last_kept_timestamp = last_seen_timestamps.get(composite_key)

        should_keep = (
            last_kept_timestamp is None
            or current_timestamp >= last_kept_timestamp + window_seconds
        )

        if should_keep:
            kept_events.append(event)
            last_seen_timestamps[composite_key] = current_timestamp

    return kept_events
