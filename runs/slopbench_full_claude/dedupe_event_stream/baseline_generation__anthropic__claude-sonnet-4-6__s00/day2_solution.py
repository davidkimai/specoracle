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
    return_stats: bool = False,
) -> list[dict] | tuple[list[dict], dict[str, int]]:
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
    return_stats : bool, optional
        When True, return a tuple of (retained_events, stats_dict) where
        stats_dict contains ``kept``, ``duplicates``, and ``malformed`` counts.
        Defaults to False.

    Returns
    -------
    list[dict]
        Retained events in their original relative order (when return_stats is False).
    tuple[list[dict], dict[str, int]]
        Retained events and a statistics dictionary with keys ``kept``,
        ``duplicates``, and ``malformed`` (when return_stats is True).
    """
    # Maps composite_key -> timestamp of the last kept event for that key
    last_kept: dict[tuple[Any, ...], int] = {}
    result: list[dict] = []

    kept = 0
    duplicates = 0
    malformed = 0

    for event in events:
        # --- Validate event structure ---
        if not isinstance(event, dict):
            malformed += 1
            continue

        # Must have a valid integer timestamp
        if "timestamp" not in event:
            malformed += 1
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            malformed += 1
            continue

        # Must contain every key field
        if not all(field in event for field in key_fields):
            malformed += 1
            continue

        # --- Build composite key ---
        composite_key = tuple(event[field] for field in key_fields)

        # --- Deduplication check ---
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if current timestamp is within the window of the kept event
            if timestamp - kept_ts < window_seconds:
                duplicates += 1
                continue  # skip duplicate

        # Keep this event and record its timestamp
        last_kept[composite_key] = timestamp
        result.append(event)
        kept += 1

    if return_stats:
        return result, {"kept": kept, "duplicates": duplicates, "malformed": malformed}
    return result
