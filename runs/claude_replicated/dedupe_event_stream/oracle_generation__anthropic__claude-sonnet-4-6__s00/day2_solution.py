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
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
    return_stats: bool = False,
) -> list[dict] | tuple[list[dict], dict[str, int]]:
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
        return_stats: If True, return a tuple of (retained_events, stats_dict)
                      where stats_dict contains 'kept', 'duplicates', and
                      'malformed' counts.

    Returns:
        List of retained events in original order, or a tuple of
        (retained_events, stats) when return_stats is True.
    """
    if not isinstance(key_fields, list):
        raise TypeError("key_fields must be a list")
    if not isinstance(window_seconds, int) or window_seconds < 0:
        raise ValueError("window_seconds must be a non-negative integer")

    # Maps composite key -> timestamp of the most recently kept event.
    kept_timestamps: dict[tuple, int] = {}
    retained: list[dict] = []

    kept_count = 0
    duplicates_count = 0
    malformed_count = 0

    for event in events:
        if not _is_valid(event):
            malformed_count += 1
            continue

        key = _extract_key(event, key_fields)
        if key is None:
            malformed_count += 1
            continue

        ts: int = event["timestamp"]

        if key in kept_timestamps:
            last_kept_ts = kept_timestamps[key]
            within_window = (ts - last_kept_ts) < window_seconds
            if within_window:
                duplicates_count += 1
                continue
            # Outside the window: this event starts a new window.

        kept_timestamps[key] = ts
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
