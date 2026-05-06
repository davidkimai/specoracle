"""
dedupe_event_stream.py

Deduplicate an event stream based on composite key fields and a rolling
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
        Sequence of event dictionaries. Each must contain an integer
        ``timestamp`` field plus every field listed in *key_fields*.
    key_fields : list[str]
        Field names that together form the composite deduplication key.
    window_seconds : int
        Duration of the rolling window in seconds.  An event is considered
        a duplicate if it shares the same composite key as a previously kept
        event **and** its timestamp falls within *window_seconds* of that
        kept event's timestamp.

    Returns
    -------
    list[dict]
        Retained events in their original relative order.
    """
    # Map composite_key -> timestamp of the most-recently *kept* event
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    for event in events:
        # --- Validation ---
        if not isinstance(event, dict):
            continue

        # timestamp must be present and be an integer
        if "timestamp" not in event:
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            continue

        # Every key field must be present
        if not all(field in event for field in key_fields):
            continue

        # --- Deduplication ---
        composite_key = tuple(event[field] for field in key_fields)

        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if within the rolling window
            if timestamp - kept_ts < window_seconds:
                continue
            # Outside the window → treat as a fresh event; update kept ts
        
        last_kept[composite_key] = timestamp
        retained.append(event)

    return retained
