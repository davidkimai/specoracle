"""
dedupe_event_stream.py

Deduplicate an event stream by composite key within a rolling timestamp window.
"""

from typing import Any


def _extract_key(event: dict, key_fields: list[str]) -> tuple[Any, ...] | None:
    """Return composite key tuple or None if any key field is missing."""
    try:
        return tuple(event[field] for field in key_fields)
    except KeyError:
        return None


def _is_valid_event(event: dict) -> bool:
    """Return True if event contains an integer timestamp."""
    return isinstance(event.get("timestamp"), int)


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> list[dict]:
    """
    Return a deduplicated list of events.

    For each composite key (formed from key_fields), keep the first occurrence
    and drop any later event whose timestamp falls within window_seconds of the
    kept event's timestamp.

    Malformed events (missing timestamp, non-integer timestamp, or missing any
    key field) are silently skipped.

    Args:
        events: Sequence of event dicts, each expected to have 'timestamp' and
                all key_fields present.
        key_fields: Field names that together form the deduplication key.
        window_seconds: Duration in seconds; events within this window after a
                        kept event share the same composite key are duplicates.

    Returns:
        Ordered list of retained (non-duplicate, well-formed) events.
    """
    if window_seconds < 0:
        raise ValueError(f"window_seconds must be non-negative, got {window_seconds}")
    if not key_fields:
        raise ValueError("key_fields must not be empty")

    # Maps composite key -> timestamp of the most-recently kept event for that key.
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    for event in events:
        if not _is_valid_event(event):
            continue

        key = _extract_key(event, key_fields)
        if key is None:
            continue

        timestamp: int = event["timestamp"]

        if key in last_kept:
            kept_timestamp = last_kept[key]
            elapsed = timestamp - kept_timestamp
            if 0 <= elapsed < window_seconds:
                # Duplicate within the rolling window; skip it.
                continue
            # Outside the window (or timestamp moved backward past the window);
            # treat as a fresh event and update the kept timestamp.

        last_kept[key] = timestamp
        retained.append(event)

    return retained
