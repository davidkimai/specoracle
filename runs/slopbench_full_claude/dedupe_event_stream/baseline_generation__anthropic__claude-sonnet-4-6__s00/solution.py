"""
dedupe_event_stream.py

Deduplicates a stream of events based on composite key fields within a rolling
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
        Ordered list of event dictionaries. Each event must have an integer
        ``timestamp`` field and every field listed in ``key_fields``.
    key_fields : list[str]
        Fields whose combined values form the composite deduplication key.
    window_seconds : int
        Duration of the rolling window in seconds. An event is a duplicate if
        it arrives within ``window_seconds`` of the most-recently *kept* event
        that shares the same composite key.

    Returns
    -------
    list[dict]
        Retained events in their original relative order.
    """
    # Maps composite_key -> timestamp of the last kept event for that key
    last_kept: dict[tuple[Any, ...], int] = {}
    result: list[dict] = []

    for event in events:
        # --- Validate event structure ---
        if not isinstance(event, dict):
            continue

        # Must have a valid integer timestamp
        if "timestamp" not in event:
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            continue

        # Must contain every key field
        if not all(field in event for field in key_fields):
            continue

        # --- Build composite key ---
        composite_key = tuple(event[field] for field in key_fields)

        # --- Deduplication check ---
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if current timestamp is within the window of the kept event
            if timestamp - kept_ts < window_seconds:
                continue  # skip duplicate

        # Keep this event and record its timestamp
        last_kept[composite_key] = timestamp
        result.append(event)

    return result
