def dedupe_events(events: list[dict], key_fields: list[str], window_seconds: int, return_stats: bool = False):
    retained = []
    last_seen: dict[tuple, int] = {}
    kept = 0
    duplicates = 0
    malformed = 0

    for event in events:
        parsed = _parse_event(event, key_fields)
        if parsed is None:
            malformed += 1
            continue
        timestamp, key = parsed
        previous = last_seen.get(key)
        if previous is not None and timestamp - previous < window_seconds:
            duplicates += 1
            continue
        retained.append(event)
        last_seen[key] = timestamp
        kept += 1

    if return_stats:
        return retained, {"kept": kept, "duplicates": duplicates, "malformed": malformed}
    return retained


def _parse_event(event: dict, key_fields: list[str]) -> tuple[int, tuple] | None:
    timestamp = event.get("timestamp")
    if not isinstance(timestamp, int):
        return None
    values = []
    for field in key_fields:
        if field not in event:
            return None
        values.append(event[field])
    return timestamp, tuple(values)
