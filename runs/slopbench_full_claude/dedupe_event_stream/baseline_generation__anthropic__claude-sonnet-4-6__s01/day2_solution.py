"""
dedupe_event_stream.py

Deduplicate an event stream based on composite key fields within a rolling
timestamp window.
"""

from typing import Any, Union


def dedupe_events(
    events: list[dict],
    key_fields: list[str],
    window_seconds: int,
    return_stats: bool = False,
) -> Union[list[dict], tuple[list[dict], dict[str, int]]]:
    """
    Deduplicate events by composite key within a rolling timestamp window.

    Parameters
    ----------
    events : list[dict]
        Sequence of event dictionaries. Each must contain an integer
        ``timestamp`` field and all fields listed in *key_fields*.
    key_fields : list[str]
        Field names that together form the composite deduplication key.
    window_seconds : int
        Duration of the deduplication window in seconds.  A later event
        whose timestamp is strictly less than ``kept_event_timestamp +
        window_seconds`` is considered a duplicate of the kept event.
    return_stats : bool, optional
        When True, return a tuple of (retained_events, stats_dict) where
        stats_dict contains counts for "kept", "duplicates", and "malformed".
        Defaults to False.

    Returns
    -------
    list[dict]
        Retained events in their original relative order (when return_stats
        is False).
    tuple[list[dict], dict[str, int]]
        A tuple of (retained_events, stats) when return_stats is True.
        stats keys: "kept", "duplicates", "malformed".
    """
    # Maps composite_key -> timestamp of the most-recently *kept* event
    # for that key.
    kept_timestamps: dict[tuple[Any, ...], int] = {}

    retained: list[dict] = []
    count_kept = 0
    count_duplicates = 0
    count_malformed = 0

    for event in events:
        # --- Validate the event ---
        if not isinstance(event, dict):
            count_malformed += 1
            continue

        # Must have an integer timestamp
        if "timestamp" not in event:
            count_malformed += 1
            continue
        ts = event["timestamp"]
        if not isinstance(ts, int):
            count_malformed += 1
            continue

        # Must contain every key field
        if not all(field in event for field in key_fields):
            count_malformed += 1
            continue

        # Build the composite key (preserve field order for determinism)
        composite_key: tuple[Any, ...] = tuple(event[f] for f in key_fields)

        # --- Deduplication check ---
        if composite_key in kept_timestamps:
            kept_ts = kept_timestamps[composite_key]
            # Duplicate if within [kept_ts, kept_ts + window_seconds)
            if ts < kept_ts + window_seconds:
                count_duplicates += 1
                continue  # drop duplicate

        # Keep this event and record its timestamp as the new anchor
        kept_timestamps[composite_key] = ts
        retained.append(event)
        count_kept += 1

    if return_stats:
        stats: dict[str, int] = {
            "kept": count_kept,
            "duplicates": count_duplicates,
            "malformed": count_malformed,
        }
        return retained, stats

    return retained
