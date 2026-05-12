"""
dedupe_event_stream.py

Deduplicate a stream of events based on composite key fields and a rolling
timestamp window.
"""


def _extract_key(event: dict, key_fields: list[str]) -> tuple | None:
    """Return composite key tuple or None if the event is malformed."""
    if not isinstance(event.get("timestamp"), int):
        return None
    try:
        return tuple(event[field] for field in key_fields)
    except KeyError:
        return None


def _is_duplicate(ts: int, last_kept: int | None, window_seconds: int) -> bool:
    """Return True if this event is a duplicate within the window."""
    if last_kept is None:
        return False
    return ts < last_kept + window_seconds


def _validate_inputs(key_fields: list[str], window_seconds: int) -> None:
    """Raise on invalid arguments."""
    if window_seconds < 0:
        raise ValueError("window_seconds must be non-negative")
    if not isinstance(key_fields, list) or not all(isinstance(f, str) for f in key_fields):
        raise TypeError("key_fields must be a list of strings")


def dedupe_events(
    events: list[dict], key_fields: list[str], window_seconds: int
) -> list[dict]:
    """
    Keep the first event for each composite key within a rolling timestamp
    window.

    Parameters
    ----------
    events : list[dict]
        Ordered sequence of event dicts. Each must have an integer 'timestamp'
        and all fields listed in key_fields.
    key_fields : list[str]
        Fields that together form the composite deduplication key.
    window_seconds : int
        Duration of the deduplication window. A later event is considered a
        duplicate if its timestamp is strictly less than
        (kept_event_timestamp + window_seconds).

    Returns
    -------
    list[dict]
        Retained events in original order.
    """
    _validate_inputs(key_fields, window_seconds)

    kept_timestamps: dict[tuple, int] = {}
    retained: list[dict] = []

    for event in events:
        key = _extract_key(event, key_fields)
        if key is None:
            continue

        ts: int = event["timestamp"]
        if _is_duplicate(ts, kept_timestamps.get(key), window_seconds):
            continue

        kept_timestamps[key] = ts
        retained.append(event)

    return retained
