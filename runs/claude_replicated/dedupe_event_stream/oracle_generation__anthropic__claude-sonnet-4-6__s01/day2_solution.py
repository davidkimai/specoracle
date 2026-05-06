"""
dedupe_event_stream: deduplicate a stream of events within a rolling time window.
"""

from typing import Any


def _extract_key(event: dict, key_fields: list[str]) -> tuple[Any, ...] | None:
    """Return the composite key tuple, or None if any field is missing."""
    try:
        return tuple(event[field] for field in key_fields)
    except KeyError:
        return None


def _is_valid_event(event: dict, key_fields: list[str]) -> bool:
    """Return True when the event has an integer timestamp and all key fields."""
    if not isinstance(event.get("timestamp"), int):
        return False
    if _extract_key(event, key_fields) is None:
        return False
    return True


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
    return_stats: bool = False,
) -> list[dict] | tuple[list[dict], dict[str, int]]:
    """
    Deduplicate events by composite key within a rolling timestamp window.

    Keep the first occurrence of each (composite key, window) combination.
    A later event is a duplicate when it shares the same composite key and
    its timestamp is less than window_seconds after the timestamp of the
    already-kept event for that key.

    Malformed events (missing timestamp, non-integer timestamp, or missing
    key fields) are silently skipped.

    Parameters
    ----------
    events:
        Ordered sequence of event dictionaries.
    key_fields:
        Field names that together form the deduplication key.
    window_seconds:
        Duration in seconds for which a kept event suppresses duplicates.
    return_stats:
        When True, return a tuple of (retained_events, stats_dict) where
        stats_dict contains "kept", "duplicates", and "malformed" counts.

    Returns
    -------
    list[dict]
        Retained events in their original relative order (when return_stats
        is False).
    tuple[list[dict], dict[str, int]]
        Retained events and a statistics dictionary (when return_stats is
        True).
    """
    if not isinstance(window_seconds, int) or window_seconds < 0:
        raise ValueError("window_seconds must be a non-negative integer")
    if not isinstance(key_fields, list) or not key_fields:
        raise ValueError("key_fields must be a non-empty list")

    # Maps composite key -> timestamp of the most recently kept event.
    kept_timestamps: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    kept_count = 0
    duplicates_count = 0
    malformed_count = 0

    for event in events:
        if not _is_valid_event(event, key_fields):
            malformed_count += 1
            continue

        composite_key = _extract_key(event, key_fields)
        ts: int = event["timestamp"]

        last_kept = kept_timestamps.get(composite_key)

        if last_kept is None or ts - last_kept >= window_seconds:
            kept_timestamps[composite_key] = ts
            retained.append(event)
            kept_count += 1
        else:
            duplicates_count += 1

    if return_stats:
        stats: dict[str, int] = {
            "kept": kept_count,
            "duplicates": duplicates_count,
            "malformed": malformed_count,
        }
        return retained, stats

    return retained
