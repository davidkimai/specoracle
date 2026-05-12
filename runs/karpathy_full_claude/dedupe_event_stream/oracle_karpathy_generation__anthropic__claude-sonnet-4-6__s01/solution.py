def dedupe_events(events: list[dict], key_fields: list[str], window_seconds: int) -> list[dict]:
    """
    Keep the first event for each composite key within a rolling timestamp window.
    
    A duplicate is any later event with the same composite key whose timestamp
    is less than window_seconds after the most recently kept event for that key.
    Malformed events (missing 'timestamp' or any key field, or non-integer timestamp) are skipped.
    """
    seen = {}  # composite_key -> timestamp of the kept event
    result = []

    for event in events:
        # Validate event has integer timestamp
        if "timestamp" not in event:
            continue
        ts = event["timestamp"]
        if not isinstance(ts, int):
            continue

        # Validate all key fields are present
        if not all(field in event for field in key_fields):
            continue

        composite_key = tuple(event[field] for field in key_fields)

        if composite_key not in seen:
            seen[composite_key] = ts
            result.append(event)
        else:
            kept_ts = seen[composite_key]
            if ts - kept_ts >= window_seconds:
                # Outside the window, treat as new event
                seen[composite_key] = ts
                result.append(event)
            # else: duplicate within window, skip

    return result
