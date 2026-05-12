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
        ``timestamp`` field and every field named in *key_fields*.
    key_fields : list[str]
        Fields that together form the composite deduplication key.
    window_seconds : int
        Duration (in seconds) of the rolling window.  Any event whose
        composite key matches a previously kept event *and* whose timestamp
        falls within *window_seconds* of that kept event is considered a
        duplicate and discarded.

    Returns
    -------
    list[dict]
        Retained events in their original relative order.
    """
    # Maps composite_key -> timestamp of the most-recently *kept* event
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    for event in events:
        # --- Validate the event is well-formed ---
        if not isinstance(event, dict):
            continue

        # timestamp must exist and be an integer
        if "timestamp" not in event:
            continue
        ts = event["timestamp"]
        if not isinstance(ts, int):
            continue

        # every key field must be present
        if not all(field in event for field in key_fields):
            continue

        # --- Build the composite key ---
        composite_key = tuple(event[field] for field in key_fields)

        # --- Deduplication check ---
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if current event is strictly within the window
            if ts - kept_ts < window_seconds:
                continue  # discard duplicate

        # Keep this event and record its timestamp
        last_kept[composite_key] = ts
        retained.append(event)

    return retained
