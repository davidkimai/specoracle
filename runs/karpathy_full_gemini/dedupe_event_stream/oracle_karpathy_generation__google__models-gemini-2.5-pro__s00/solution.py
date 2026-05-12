import typing

def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int
) -> list[dict]:
    """
    Deduplicates a stream of events based on a composite key and a time window.

    Keeps the first event for each composite key within a rolling timestamp window.
    An event is a dictionary that must contain an integer 'timestamp' field and
    all fields listed in `key_fields`. Events that do not meet this structure,
    or have unhashable values in their key fields, are considered malformed and
    are skipped.

    A duplicate is defined as any subsequent event that has the same composite
    key and a timestamp less than `window_seconds` after the timestamp of the
    last kept event with that same key.

    The relative order of the retained events is preserved from the input list.

    Args:
        events: A list of dictionaries, where each dictionary is an event.
        key_fields: A list of strings representing the dictionary keys that
                    form the composite key for deduplication.
        window_seconds: An integer representing the duration of the deduplication
                        window in seconds.

    Returns:
        A new list of event dictionaries with duplicates removed.
    """
    # Stores the timestamp of the last kept event for each composite key.
    # The key is a tuple of values from the event's key_fields, and the
    # value is the integer timestamp.
    last_kept_timestamps: dict[tuple, int] = {}
    
    # The list of events to be returned, with duplicates filtered out.
    deduplicated_events: list[dict] = []

    for event in events:
        # --- 1. Validate Event Structure ---
        # Skip if 'timestamp' is missing or not an integer.
        timestamp = event.get('timestamp')
        if not isinstance(timestamp, int):
            continue

        # Skip if any of the key_fields are missing.
        if not all(key in event for key in key_fields):
            continue

        try:
            # --- 2. Construct Composite Key ---
            # The composite key is a tuple of the values from the key_fields.
            composite_key = tuple(event[key] for key in key_fields)

            # --- 3. Apply Deduplication Logic ---
            last_kept_timestamp = last_kept_timestamps.get(composite_key)

            if last_kept_timestamp is None:
                # First time seeing this composite key. Keep the event and
                # record its timestamp as the start of a new window.
                deduplicated_events.append(event)
                last_kept_timestamps[composite_key] = timestamp
            elif timestamp >= last_kept_timestamp + window_seconds:
                # A previous event with this key was seen, but the window has
                # expired. Keep this new event and reset the window.
                deduplicated_events.append(event)
                last_kept_timestamps[composite_key] = timestamp
            # else: The event is within the window of a previously kept event
            # with the same key, so it is a duplicate. Skip it.

        except (KeyError, TypeError):
            # KeyError: Defensive; the check above should prevent this.
            # TypeError: Occurs if the composite_key contains unhashable types
            # (e.g., a list or dict). Such events are considered malformed.
            continue

    return deduplicated_events
