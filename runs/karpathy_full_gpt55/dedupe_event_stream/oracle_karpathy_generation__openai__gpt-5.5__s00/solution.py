def dedupe_events(events: list[dict], key_fields: list[str], window_seconds: int) -> list[dict]:
    """
    Return retained events after de-duplicating by composite key.

    Assumptions:
    - The timestamp field is named "timestamp".
    - Events are processed in input order.
    - For each composite key, the kept timestamp starts a window.
      A later event with the same key is skipped when
      event["timestamp"] - kept_timestamp < window_seconds.
    - Malformed events are skipped.
    """
    retained = []
    kept_timestamps = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            continue

        if any(field not in event for field in key_fields):
            continue

        key = tuple(event[field] for field in key_fields)

        try:
            last_timestamp = kept_timestamps.get(key)
        except TypeError:
            continue

        if last_timestamp is None or timestamp - last_timestamp >= window_seconds:
            retained.append(event)
            kept_timestamps[key] = timestamp

    return retained
