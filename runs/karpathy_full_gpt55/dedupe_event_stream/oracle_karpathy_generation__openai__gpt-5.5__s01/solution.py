"""Deduplicate timestamped event streams."""


_MISSING = object()


def dedupe_events(events: list[dict], key_fields: list[str], window_seconds: int) -> list[dict]:
    """Keep the first well-formed event per composite key in each rolling window."""
    retained = []
    kept_timestamps = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            continue

        try:
            key = tuple(event[field] for field in key_fields)
        except KeyError:
            continue

        try:
            previous_timestamp = kept_timestamps.get(key, _MISSING)
        except TypeError:
            continue

        if previous_timestamp is not _MISSING and timestamp < previous_timestamp + window_seconds:
            continue

        kept_timestamps[key] = timestamp
        retained.append(event)

    return retained
