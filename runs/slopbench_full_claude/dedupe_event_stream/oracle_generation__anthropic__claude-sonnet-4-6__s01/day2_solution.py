"""
dedupe_event_stream: Remove duplicate events within a rolling timestamp window.
"""

from typing import Any


def _extract_key(event: dict, key_fields: list[str]) -> tuple | None:
    """Return a composite key tuple or None if the event is malformed."""
    try:
        return tuple(event[field] for field in key_fields)
    except KeyError:
        return None


def _is_valid_event(event: dict) -> bool:
    """Return True if the event contains an integer timestamp."""
    return isinstance(event.get("timestamp"), int)


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
    return_stats: bool = False,
) -> list[dict] | tuple[list[dict], dict[str, int]]:
    """
    Return a deduplicated list of events.

    The first event seen for each composite key is kept. Any later event with
    the same composite key whose timestamp falls within window_seconds of the
    kept event's timestamp is considered a duplicate and dropped.

    Args:
        events: Sequence of event dicts, each expected to have 'timestamp'
                (int) and all fields named in key_fields.
        key_fields: Field names that form the composite deduplication key.
        window_seconds: Duration in seconds defining the deduplication window.
        return_stats: When True, return a tuple of (retained_events, stats_dict)
                      where stats_dict contains 'kept', 'duplicates', and
                      'malformed' counts.

    Returns:
        Ordered list of retained (non-duplicate) events, or a tuple of that
        list and a stats dict when return_stats is True.

    Raises:
        TypeError: If events is not a list or key_fields is not a list.
        ValueError: If window_seconds is negative.
    """
    if not isinstance(events, list):
        raise TypeError(f"events must be a list, got {type(events).__name__}")
    if not isinstance(key_fields, list):
        raise TypeError(f"key_fields must be a list, got {type(key_fields).__name__}")
    if window_seconds < 0:
        raise ValueError(f"window_seconds must be non-negative, got {window_seconds}")

    # Maps composite key -> timestamp of the kept event.
    kept_timestamps: dict[tuple, int] = {}
    retained: list[dict] = []

    kept_count = 0
    duplicates_count = 0
    malformed_count = 0

    for event in events:
        if not isinstance(event, dict):
            malformed_count += 1
            continue
        if not _is_valid_event(event):
            malformed_count += 1
            continue

        key = _extract_key(event, key_fields)
        if key is None:
            malformed_count += 1
            continue

        timestamp: int = event["timestamp"]

        if key in kept_timestamps:
            kept_ts = kept_timestamps[key]
            if timestamp - kept_ts < window_seconds:
                # Within the deduplication window; drop this event.
                duplicates_count += 1
                continue
            # Outside the window; treat as a new first occurrence.

        kept_timestamps[key] = timestamp
        retained.append(event)
        kept_count += 1

    if return_stats:
        stats = {
            "kept": kept_count,
            "duplicates": duplicates_count,
            "malformed": malformed_count,
        }
        return retained, stats

    return retained
