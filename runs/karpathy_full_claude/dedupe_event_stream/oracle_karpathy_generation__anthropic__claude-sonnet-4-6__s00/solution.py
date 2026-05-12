def dedupe_events(events: list[dict], key_fields: list[str], window_seconds: int) -> list[dict]:
    seen = {}
    result = []
    for event in events:
        if "timestamp" not in event or not isinstance(event["timestamp"], int):
            continue
        if any(k not in event for k in key_fields):
            continue
        composite_key = tuple(event[k] for k in key_fields)
        ts = event["timestamp"]
        if composite_key in seen:
            last_ts = seen[composite_key]
            if ts - last_ts < window_seconds:
                continue
        seen[composite_key] = ts
        result.append(event)
    return result
