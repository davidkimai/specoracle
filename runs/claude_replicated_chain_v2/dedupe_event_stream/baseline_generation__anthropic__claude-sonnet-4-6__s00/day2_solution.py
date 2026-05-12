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
    return_stats: bool = False,
) -> list[dict] | tuple[list[dict], dict[str, int]]:
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
    return_stats : bool, optional
        When True, return a tuple of (retained_events, stats_dict) where
        stats_dict contains "kept", "duplicates", and "malformed" counts.
        Defaults to False.

    Returns
    -------
    list[dict]
        Retained events in their original relative order (when return_stats
        is False).
    tuple[list[dict], dict[str, int]]
        Retained events and a statistics dictionary with keys "kept",
        "duplicates", and "malformed" (when return_stats is True).
    """
    # Map composite_key -> timestamp of the most-recently *kept* event
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []
    kept_count = 0
    duplicates_count = 0
    malformed_count = 0

    for event in events:
        # --- Validation ---
        if not isinstance(event, dict):
            malformed_count += 1
            continue

        # timestamp must be present and be an integer
        if "timestamp" not in event:
            malformed_count += 1
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            malformed_count += 1
            continue

        # Every key field must be present
        if not all(field in event for field in key_fields):
            malformed_count += 1
            continue

        # --- Deduplication ---
        composite_key = tuple(event[field] for field in key_fields)

        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if within the rolling window
            if timestamp - kept_ts < window_seconds:
                duplicates_count += 1
                continue
            # Outside the window → treat as a fresh event; update kept ts

        last_kept[composite_key] = timestamp
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
