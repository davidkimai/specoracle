"""
This module provides functionality to deduplicate a stream of events.
"""

import typing

def dedupe_events(
    events: typing.List[typing.Dict[str, typing.Any]],
    key_fields: typing.List[str],
    window_seconds: int
) -> typing.List[typing.Dict[str, typing.Any]]:
    """Deduplicates events based on a composite key and a rolling time window.

    This function processes a list of event dictionaries, keeping only the first
    occurrence of an event for a given composite key within a specified time
    window. The order of the retained events from the original list is
    preserved.

    An event is considered a duplicate if it has the same composite key as a
    previously kept event and its timestamp is within `window_seconds` of that
    kept event's timestamp.

    Events that are not dictionaries, or that lack an integer 'timestamp' field,
    or are missing any of the specified `key_fields`, are considered malformed
    and are skipped. Events with unhashable values in their key fields are also
    skipped.

    Args:
        events: A list of dictionaries, where each dictionary represents an
            event.
        key_fields: A list of string keys that together form the composite key
            for deduplication.
        window_seconds: The duration of the deduplication window in seconds. An
            event is a duplicate if its timestamp is less than `window_seconds`
            after a kept event with the same key.

    Returns:
        A new list of event dictionaries containing the unique events in their
        original order.
    """
    # Maps a composite key to the timestamp of the last event that was kept.
    last_kept_timestamps: typing.Dict[typing.Tuple[typing.Any, ...], int] = {}
    deduplicated_events: typing.List[typing.Dict[str, typing.Any]] = []

    for event in events:
        # 1. Validate the event structure and timestamp.
        if not isinstance(event, dict):
            continue

        timestamp = event.get('timestamp')
        if not isinstance(timestamp, int):
            continue

        # 2. Extract composite key and perform deduplication.
        try:
            # Create a tuple of values corresponding to the key_fields.
            composite_key = tuple(event[key] for key in key_fields)

            # The dictionary operations below will raise a TypeError if the
            # composite_key contains unhashable types (e.g., lists or dicts).
            last_kept_timestamp = last_kept_timestamps.get(composite_key)

            if last_kept_timestamp is None:
                # This is the first time we have seen this composite key.
                # Keep the event and record its timestamp.
                deduplicated_events.append(event)
                last_kept_timestamps[composite_key] = timestamp
            else:
                # We have seen this key before. Check if the current event is
                # outside the deduplication window.
                if timestamp >= last_kept_timestamp + window_seconds:
                    # This event is not a duplicate, so we keep it and update
                    # the window's start time for this key.
                    deduplicated_events.append(event)
                    last_kept_timestamps[composite_key] = timestamp
                # Otherwise, the event is within the window and is a duplicate.
                # We discard it by doing nothing.

        except (KeyError, TypeError):
            # This event is malformed because it's missing a key field
            # or contains an unhashable value for a key field. Skip it.
            continue

    return deduplicated_events
