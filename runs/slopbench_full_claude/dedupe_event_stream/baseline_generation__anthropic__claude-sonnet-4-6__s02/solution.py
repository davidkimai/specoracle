"""
dedupe_event_stream.py

Deduplicates an event stream based on composite key fields and a rolling
timestamp window.
"""

from typing import Any


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
) -> list[dict]:
    """
    Deduplicate events by composite key within a rolling timestamp window.

    Parameters
    ----------
    events : list[dict]
        Sequence of event dictionaries.  Each event must contain an integer
        ``timestamp`` field and every field listed in *key_fields*.
    key_fields : list[str]
        Field names that together form the composite deduplication key.
    window_seconds : int
        Duration (in seconds) of the rolling window.  An event is considered
        a duplicate when it shares the same composite key as a previously kept
        event **and** its timestamp falls within *window_seconds* of that kept
        event's timestamp.

    Returns
    -------
    list[dict]
        Retained events in their original relative order.
    """
    # Maps composite key -> timestamp of the most-recently *kept* event.
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    for event in events:
        # --- Validate event structure ---
        if not isinstance(event, dict):
            continue

        # Timestamp must be present and integer.
        if "timestamp" not in event:
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            continue

        # All key fields must be present.
        if not all(field in event for field in key_fields):
            continue

        # Build the composite key (hashable tuple).
        composite_key: tuple[Any, ...] = tuple(event[field] for field in key_fields)

        # --- Deduplication logic ---
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if within the window (strictly less than window_seconds
            # after the kept event).
            if timestamp - kept_ts < window_seconds:
                continue  # Drop duplicate.
            # Outside the window: treat as a new, non-duplicate event.

        # Keep this event and record its timestamp.
        last_kept[composite_key] = timestamp
        retained.append(event)

    return retained
