"""Deduplicate event streams by composite key and timestamp window."""

__all__ = ["dedupe_events"]


def _is_integer_timestamp(value):
    """Return True only for plain integer timestamps, excluding booleans."""
    return type(value) is int


def _is_duplicate_timestamp(timestamp, kept_timestamps, window_seconds):
    """
    A timestamp is a duplicate if it falls in [kept, kept + window_seconds)
    for any previously retained event with the same composite key.
    """
    for kept_timestamp in kept_timestamps:
        delta = timestamp - kept_timestamp
        if 0 <= delta < window_seconds:
            return True
    return False


def _get_timestamp_bucket(composite_key, hash_buckets, equality_buckets):
    """
    Return the retained timestamp list for a composite key.

    Hashable composite keys use a dictionary. Unhashable composite keys are
    supported with a small equality-scanned fallback so key values such as
    lists remain usable when they compare normally.
    """
    try:
        hash(composite_key)
    except Exception:
        for stored_key, timestamps in equality_buckets:
            try:
                if stored_key == composite_key:
                    return timestamps
            except Exception:
                continue

        timestamps = []
        equality_buckets.append((composite_key, timestamps))
        return timestamps

    try:
        return hash_buckets.setdefault(composite_key, [])
    except Exception:
        for stored_key, timestamps in equality_buckets:
            try:
                if stored_key == composite_key:
                    return timestamps
            except Exception:
                continue

        timestamps = []
        equality_buckets.append((composite_key, timestamps))
        return timestamps


def dedupe_events(events: list[dict], key_fields: list[str], window_seconds: int) -> list[dict]:
    """
    Keep the first well-formed event for each composite key within a timestamp
    window.

    Malformed events are skipped. A well-formed event is a dictionary containing
    a plain integer "timestamp" field and all requested key fields.
    """
    retained = []
    hash_buckets = {}
    equality_buckets = []

    for event in events:
        if not isinstance(event, dict):
            continue

        timestamp = event.get("timestamp")
        if not _is_integer_timestamp(timestamp):
            continue

        missing_key_field = False
        for field in key_fields:
            if field not in event:
                missing_key_field = True
                break
        if missing_key_field:
            continue

        composite_key = tuple(event[field] for field in key_fields)
        kept_timestamps = _get_timestamp_bucket(
            composite_key,
            hash_buckets,
            equality_buckets,
        )

        if _is_duplicate_timestamp(timestamp, kept_timestamps, window_seconds):
            continue

        retained.append(event)
        kept_timestamps.append(timestamp)

    return retained
