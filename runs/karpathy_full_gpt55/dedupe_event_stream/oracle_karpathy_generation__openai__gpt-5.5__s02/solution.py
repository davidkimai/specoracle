def dedupe_events(events: list[dict], key_fields: list[str], window_seconds: int) -> list[dict]:
    """Return valid events with later duplicates removed.

    The timestamp field is assumed to be named "timestamp". Each per-key window is
    anchored at the most recent retained event for that composite key.
    """
    retained = []
    windows = []

    for event in events:
        if not isinstance(event, dict):
            continue
        if "timestamp" not in event:
            continue

        timestamp = event["timestamp"]
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            continue

        key_values = []
        malformed = False
        for field in key_fields:
            if field not in event:
                malformed = True
                break
            key_values.append(event[field])
        if malformed:
            continue

        composite_key = tuple(key_values)
        window_index = None
        kept_timestamp = None

        for index, (known_key, known_timestamp) in enumerate(windows):
            if known_key == composite_key:
                window_index = index
                kept_timestamp = known_timestamp
                break

        if window_index is not None and timestamp < kept_timestamp + window_seconds:
            continue

        retained.append(event)

        if window_index is None:
            windows.append((composite_key, timestamp))
        else:
            windows[window_index] = (composite_key, timestamp)

    return retained
