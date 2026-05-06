"""
dedupe_event_stream.py

Deduplicate a stream of events based on composite key fields and a rolling
timestamp window.
"""

from typing import Any


def _extract_key(event: dict, key_fields: list[str]) -> tuple | None:
    """Return a hashable composite key or None if any field is missing."""
    try:
        return tuple(event[field] for field in key_fields)
    except KeyError:
        return None


def _is_valid(event: dict) -> bool:
    """Return True if event contains an integer 'timestamp' field."""
    return isinstance(event.get("timestamp"), int)


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
        Field names that form the composite deduplication key.
    window_seconds:
        Duration of the deduplication window in seconds.

    Returns
    -------
    list[dict]
        Retained events in their original order.
    """
    if not isinstance(key_fields, list) or not key_fields:
        raise ValueError("key_fields must be a non-empty list")
    if not isinstance(window_seconds, int) or window_seconds < 0:
        raise ValueError("window_seconds must be a non-negative integer")

    # Maps composite key -> timestamp of the most recently kept event.
    seen: dict[tuple, int] = {}
    retained: list[dict] = []

    for event in events:
        if not _is_valid(event):
            continue

        key = _extract_key(event, key_fields)
        if key is None:
            continue

        ts: int = event["timestamp"]

        if key in seen:
            kept_ts = seen[key]
            if ts - kept_ts < window_seconds:
                # Duplicate within the window; skip.
                continue
            # Outside the window; treat as a new event and update the anchor.

        seen[key] = ts
        retained.append(event)

    return retained
