"""
dedupe_event_stream.py

Deduplicates an event stream based on composite key fields within a rolling
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
        Sequence of event dictionaries. Each event must contain an integer
        ``timestamp`` field and all fields listed in *key_fields*.
    key_fields : list[str]
        Field names that together form the composite deduplication key.
    window_seconds : int
        Duration (in seconds) of the rolling window. An event is considered a
        duplicate when it shares the same composite key as a previously kept
        event **and** its timestamp is strictly less than
        ``kept_event_timestamp + window_seconds``.

    Returns
    -------
    list[dict]
        Retained events in their original relative order, with duplicates
        removed.
    """
    # Maps composite key -> timestamp of the most-recently *kept* event.
    last_kept: dict[tuple[Any, ...], int] = {}
    result: list[dict] = []

    for event in events:
        # --- Validation ---
        if not isinstance(event, dict):
            continue

        # timestamp must be present and integer
        if "timestamp" not in event:
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            continue

        # All key fields must be present
        if not all(field in event for field in key_fields):
            continue

        # --- Composite key ---
        composite_key = tuple(event[field] for field in key_fields)

        # --- Deduplication check ---
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            if timestamp < kept_ts + window_seconds:
                # This event is a duplicate within the window; skip it.
                continue
            # Outside the window: treat as a new "first" occurrence.

        # Keep this event.
        last_kept[composite_key] = timestamp
        result.append(event)

    return result
