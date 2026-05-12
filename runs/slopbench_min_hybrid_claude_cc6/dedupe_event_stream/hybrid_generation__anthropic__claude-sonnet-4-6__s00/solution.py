"""
dedupe_event_stream.py

Deduplicate a stream of events based on composite key fields and a rolling
timestamp window.
"""


def _extract_key(event: dict, key_fields: list[str]) -> tuple | None:
    """Return composite key tuple, or None if any field is missing."""
    try:
        return tuple(event[field] for field in key_fields)
    except KeyError:
        return None


def _has_valid_timestamp(event: dict) -> bool:
    """Return True if event contains an integer 'timestamp' field."""
    return isinstance(event.get("timestamp"), int)


def _is_usable(event: dict, key_fields: list[str]) -> bool:
    """Return True if event has a valid timestamp and all key fields present."""
    return _has_valid_timestamp(event) and _extract_key(event, key_fields) is not None


def _is_duplicate(key: tuple, ts: int, seen: dict, window_seconds: int) -> bool:
    """Return True if this key was seen recently within the window."""
    last_ts = seen.get(key)
    return last_ts is not None and ts - last_ts < window_seconds


def _validate_args(key_fields: list[str], window_seconds: int) -> None:
    """Raise ValueError for invalid arguments."""
    if not isinstance(key_fields, list) or not key_fields:
        raise ValueError("key_fields must be a non-empty list")
    if not isinstance(window_seconds, int) or window_seconds < 0:
        raise ValueError("window_seconds must be a non-negative integer")


def dedupe_events(
    events: list[dict], key_fields: list[str], window_seconds: int
) -> list[dict]:
    """
    Keep the first event for each composite key within a rolling timestamp window.

    Parameters
    ----------
    events:
        Ordered sequence of event dicts.
    key_fields:
        Fields whose combined values form the deduplication key.
    window_seconds:
        Duration in seconds during which a repeated composite key is a duplicate.

    Returns
    -------
    list[dict]
        Events with duplicates removed, in original order.
    """
    _validate_args(key_fields, window_seconds)

    seen: dict[tuple, int] = {}
    retained: list[dict] = []

    for event in events:
        if not _is_usable(event, key_fields):
            continue

        key = _extract_key(event, key_fields)
        ts: int = event["timestamp"]

        if _is_duplicate(key, ts, seen, window_seconds):
            continue

        seen[key] = ts
        retained.append(event)

    return retained
