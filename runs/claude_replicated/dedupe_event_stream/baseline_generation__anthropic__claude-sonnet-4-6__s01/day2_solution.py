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
    return_stats: bool = False,
) -> list[dict] | tuple[list[dict], dict[str, int]]:
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
    return_stats : bool, optional
        When ``True``, return a tuple of ``(retained_events, stats)`` where
        ``stats`` is a dict with keys ``"kept"``, ``"duplicates"``, and
        ``"malformed"``. Defaults to ``False``.

    Returns
    -------
    list[dict]
        Retained events in their original relative order, with duplicates
        removed (when *return_stats* is ``False``).
    tuple[list[dict], dict[str, int]]
        A tuple of retained events and a statistics dictionary (when
        *return_stats* is ``True``).
    """
    # Maps composite key -> timestamp of the most-recently *kept* event.
    last_kept: dict[tuple[Any, ...], int] = {}
    result: list[dict] = []

    kept_count = 0
    duplicates_count = 0
    malformed_count = 0

    for event in events:
        # --- Validation ---
        if not isinstance(event, dict):
            malformed_count += 1
            continue

        # timestamp must be present and integer
        if "timestamp" not in event:
            malformed_count += 1
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            malformed_count += 1
            continue

        # All key fields must be present
        if not all(field in event for field in key_fields):
            malformed_count += 1
            continue

        # --- Composite key ---
        composite_key = tuple(event[field] for field in key_fields)

        # --- Deduplication check ---
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            if timestamp < kept_ts + window_seconds:
                # This event is a duplicate within the window; skip it.
                duplicates_count += 1
                continue
            # Outside the window: treat as a new "first" occurrence.

        # Keep this event.
        last_kept[composite_key] = timestamp
        result.append(event)
        kept_count += 1

    if return_stats:
        stats = {
            "kept": kept_count,
            "duplicates": duplicates_count,
            "malformed": malformed_count,
        }
        return result, stats

    return result
