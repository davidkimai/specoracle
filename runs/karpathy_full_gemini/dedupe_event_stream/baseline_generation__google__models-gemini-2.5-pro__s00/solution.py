"""A module for deduplicating events in a stream."""

import typing

# Type alias for an event dictionary for improved readability.
Event = typing.Dict[str, typing.Any]


def dedupe_events(
    events: typing.List[Event],
    key_fields: typing.List[str],
    window_seconds: int,
) -> typing.List[Event]:
    """Filters a list of events to remove duplicates within a rolling time window.

    This function processes a list of event dictionaries, each expected to have
    an integer 'timestamp' and fields that constitute a composite key. It keeps
    the first event encountered for a given composite key. Subsequent events with
    the same composite key are considered duplicates if their timestamp falls
    within `window_seconds` of the last kept event's timestamp for that key.

    Events that are not dictionaries, lack a 'timestamp' key with an integer
    value, or are missing any of the specified `key_fields` are considered
    malformed and skipped. Events with unhashable values in their key fields
    are also skipped.

    The original order of the non-duplicate events is preserved in the output.

    Args:
        events: A list of event dictionaries.
        key_fields: A list of dictionary keys that together form the unique
                    identifier for an event type.
        window_seconds: The duration in seconds of the deduplication window.
                        An event is a duplicate if it has the same key as a
                        kept event and its timestamp is less than
                        `kept_event['timestamp'] + window_seconds`.

    Returns:
        A new list containing the events after deduplication, with their
        original order preserved.
    """
    last_kept_timestamps: typing.Dict[typing.Tuple, int] = {}
    deduplicated_events: typing.List[Event] = []

    for event in events:
        # Validate that the event is a dictionary and has an integer timestamp.
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        if not isinstance(timestamp, int):
            continue

        # Validate that all required key fields are present.
        if not all(key in event for key in key_fields):
            continue

        # Construct a hashable composite key from the specified fields.
        try:
            composite_
