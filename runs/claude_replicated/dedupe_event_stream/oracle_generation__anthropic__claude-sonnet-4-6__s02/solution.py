"""
dedupe_event_stream: Remove duplicate events within a rolling timestamp window.
"""

from typing import Any


def _extract_key(event: dict, key_fields: list[str]) -> tuple | None:
    """Return composite key tuple or None if any field is missing."""
    try:
        return tuple(event[field] for field in key_fields)
    except KeyError:
        return None


def _is_valid(event: dict) -> bool:
    """Return True if event contains an integer timestamp."""
    return isinstance(event.get("timestamp"), int)


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> list[dict]:
    """
    Deduplicate events by composite key within a rolling timestamp window.

    Keep the first occurrence of each composite key. Any subsequent event
    with the same composite key whose timestamp falls within window_seconds
    of the kept event's timestamp is considered a duplicate and discarded.

    Parameters
    ----------
    events:
        Ordered sequence of event dicts, each expected to have 'timestamp'
        (int) and all fields named in key_fields.
    key_fields:
        Field names that together form the deduplication key.
    window_seconds:
        Duration in seconds. A later event is a duplicate if its timestamp
        is less than window_seconds after the kept event's timestamp.

    Returns
    -------
    list[dict]
        Retained events in their original order.
    """
    if window_seconds < 0:
        raise ValueError(f"window_seconds must be non-negative, got {window_seconds}")
    if not isinstance(key_fields, list) or not key_fields:
        raise ValueError("key_fields must be a non-empty list")

    # Maps composite key -> timestamp of the most recently kept event.
    kept_timestamps: dict[tuple, int] = {}
    retained: list[dict] = []

    for event in events:
        if not _is_valid(event):
            continue

        key = _extract_key(event, key_fields)
        if key is None:
            continue

        timestamp: int = event["timestamp"]

        if key in kept_timestamps:
            kept_at = kept_timestamps[key]
            elapsed = timestamp - kept_at
            if 0 <= elapsed < window_seconds:
                # Duplicate within the window; discard.
                continue
            # Outside the window (or timestamp went backwards relative to kept):
            # treat as a new event and update the kept timestamp.

        kept_timestamps[key] = timestamp
        retained.append(event)

    return retained
