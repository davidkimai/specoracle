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
        Input event stream. Each event should contain an integer 'timestamp'
        and all fields listed in key_fields.
    key_fields : list[str]
        Fields used to form the composite deduplication key.
    window_seconds : int
        Duration (in seconds) of the rolling window. An event is considered a
        duplicate if it shares the same composite key and its timestamp is
        strictly less than window_seconds after the timestamp of the
        previously-kept event with that key.

    Returns
    -------
    list[dict]
        Retained events in their original relative order.
    """
    # Maps composite key -> timestamp of the most recently kept event
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    for event in events:
        # Validate: must be a dict
        if not isinstance(event, dict):
            continue

        # Validate: must have an integer 'timestamp'
        if "timestamp" not in event:
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            continue

        # Validate: must contain every key field
        if not all(field in event for field in key_fields):
            continue

        # Build composite key (order follows key_fields)
        composite_key = tuple(event[field] for field in key_fields)

        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if current timestamp is within the window
            if timestamp - kept_ts < window_seconds:
                continue
            # Outside the window — treat as a fresh event; update kept timestamp
            last_kept[composite_key] = timestamp
        else:
            # First occurrence of this composite key
            last_kept[composite_key] = timestamp

        retained.append(event)

    return retained
