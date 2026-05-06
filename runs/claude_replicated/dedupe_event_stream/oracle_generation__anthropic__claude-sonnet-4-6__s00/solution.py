"""
dedupe_event_stream: Remove duplicate events within a rolling timestamp window.
"""

from typing import Any


def _extract_key(event: dict, key_fields: list[str]) -> tuple | None:
    """Return composite key tuple, or None if any field is missing."""
    try:
        return tuple(event[field] for field in key_fields)
    except KeyError:
        return None


def _is_valid(event: dict) -> bool:
    """Return True if event has an integer timestamp."""
    ts = event.get("timestamp")
    return isinstance(ts, int)


def dedupe_events(
    events: list[dict], key_fields: list[str], window_seconds: int
) -> list[dict]:
    """
    Deduplicate events by composite key within a rolling timestamp window.

    Keeps the first occurrence of each composite key. Any subsequent event
    with the same composite key whose timestamp falls within window_seconds
    of the kept event's timestamp is considered a duplicate and discarded.

    Args:
        events: Sequence of event dicts, each expected to have 'timestamp'
                (int) and all key_fields present.
        key_fields: Field names that together form the composite dedup key.
        window_seconds: Duration in seconds defining the dedup window.

    Returns:
        List of retained events in original order.
    """
    if not isinstance(key_fields, list):
        raise TypeError("key_fields must be a list")
    if not isinstance(window_seconds, int) or window_seconds < 0:
        raise ValueError("window_seconds must be a non-negative integer")

    # Maps composite key -> timestamp of the most recently kept event.
    kept_timestamps: dict[tuple, int] = {}
    retained: list[dict] = []

    for event in events:
        if not _is_valid(event):
            continue

        key = _extract_key(event, key_fields)
        if key is None:
            continue

        ts: int = event["timestamp"]

        if key in kept_timestamps:
            last_kept_ts = kept_timestamps[key]
            within_window = (ts - last_kept_ts) < window_seconds
            if within_window:
                continue
            # Outside the window: this event starts a new window.

        kept_timestamps[key] = ts
        retained.append(event)

    return retained
