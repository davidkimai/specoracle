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
        Sequence of event dictionaries. Each event must have an integer
        ``timestamp`` field and all fields listed in *key_fields*.
    key_fields : list[str]
        Field names that form the composite deduplication key.
    window_seconds : int
        Duration (in seconds) of the deduplication window.  A later event
        whose timestamp falls within [kept_ts, kept_ts + window_seconds) for
        the same composite key is considered a duplicate and is discarded.

    Returns
    -------
    list[dict]
        Retained events in their original relative order.
    """
    # Maps composite key -> timestamp of the most-recently *kept* event
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    for event in events:
        # --- Validate event structure ---
        if not isinstance(event, dict):
            continue

        # Validate timestamp
        if "timestamp" not in event:
            continue
        ts = event["timestamp"]
        if not isinstance(ts, int):
            continue

        # Validate all key fields are present
        missing = any(field not in event for field in key_fields)
        if missing:
            continue

        # Build composite key (order follows key_fields)
        composite_key = tuple(event[field] for field in key_fields)

        # Check deduplication window
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if ts is within [kept_ts, kept_ts + window_seconds)
            if kept_ts <= ts < kept_ts + window_seconds:
                continue  # discard duplicate

        # Keep this event and record its timestamp
        last_kept[composite_key] = ts
        retained.append(event)

    return retained
