"""
dedupe_event_stream.py

Deduplicates an event stream based on composite key fields and a rolling
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
        Sequence of event dictionaries.  Each event must contain an integer
        ``timestamp`` field and every field listed in *key_fields*.
    key_fields : list[str]
        Field names that together form the composite deduplication key.
    window_seconds : int
        Duration (in seconds) of the rolling window.  An event is considered
        a duplicate when it shares the same composite key as a previously kept
        event **and** its timestamp falls within *window_seconds* of that kept
        event's timestamp.
    return_stats : bool, optional
        When ``True``, return a tuple of ``(retained_events, stats)`` where
        ``stats`` is a dict with keys ``"kept"``, ``"duplicates"``, and
        ``"malformed"``.  Defaults to ``False``.

    Returns
    -------
    list[dict]
        Retained events in their original relative order (when
        ``return_stats`` is ``False``).
    tuple[list[dict], dict[str, int]]
        A ``(retained_events, stats)`` pair when ``return_stats`` is ``True``.
    """
    # Maps composite key -> timestamp of the most-recently *kept* event.
    last_kept: dict[tuple[Any, ...], int] = {}
    retained: list[dict] = []

    kept_count = 0
    duplicates_count = 0
    malformed_count = 0

    for event in events:
        # --- Validate event structure ---
        if not isinstance(event, dict):
            malformed_count += 1
            continue

        # Timestamp must be present and integer.
        if "timestamp" not in event:
            malformed_count += 1
            continue
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            malformed_count += 1
            continue

        # All key fields must be present.
        if not all(field in event for field in key_fields):
            malformed_count += 1
            continue

        # Build the composite key (hashable tuple).
        composite_key: tuple[Any, ...] = tuple(event[field] for field in key_fields)

        # --- Deduplication logic ---
        if composite_key in last_kept:
            kept_ts = last_kept[composite_key]
            # Duplicate if within the window (strictly less than window_seconds
            # after the kept event).
            if timestamp - kept_ts < window_seconds:
                duplicates_count += 1
                continue  # Drop duplicate.
            # Outside the window: treat as a new, non-duplicate event.

        # Keep this event and record its timestamp.
        last_kept[composite_key] = timestamp
        retained.append(event)
        kept_count += 1

    if return_stats:
        stats: dict[str, int] = {
            "kept": kept_count,
            "duplicates": duplicates_count,
            "malformed": malformed_count,
        }
        return retained, stats

    return retained
