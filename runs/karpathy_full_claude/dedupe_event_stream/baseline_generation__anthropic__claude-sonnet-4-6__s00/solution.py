"""
dedupe_event_stream.py

Deduplicate a stream of events based on composite key fields and a rolling
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
        Duration of the deduplication window in seconds.  An event is
        considered a duplicate if it shares the same composite key and its
        timestamp is strictly less than ``window_seconds`` after the timestamp
        of the most-recently *kept* event for that key.

    Returns
    -------
    list[dict]
        Retained events in their original relative order.
    """
    # Maps composite key -> timestamp of the last kept event for that key.
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    for event in events:
        # --- Validate the event ---
        if not isinstance(event, dict):
            continue

        # timestamp must be present and be an integer
        if "timestamp" not in event:
            continue
        ts = event["timestamp"]
        if not isinstance(ts, int):
            continue

        # All key fields must be present
        if not all(field in event for field in key_fields):
            continue

        # Build the composite key (order matches key_fields)
        composite_key = tuple(event[field] for field in key_fields)

        # --- Deduplication check ---
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if the new event's timestamp is within the window
            # (i.e. ts - kept_ts < window_seconds  =>  ts < kept_ts + window_seconds)
            if ts - kept_ts < window_seconds:
                continue  # skip duplicate

        # Keep this event and record its timestamp
        last_kept[composite_key] = ts
        retained.append(event)

    return retained
