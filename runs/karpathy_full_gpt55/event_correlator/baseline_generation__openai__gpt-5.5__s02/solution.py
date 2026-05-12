"""Event correlation utilities."""

from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict
from datetime import timedelta
from typing import Any


def _is_within(start: Any, end: Any, limit_seconds: int) -> bool:
    """Return whether end - start is no more than limit_seconds."""
    delta = end - start
    if isinstance(delta, timedelta):
        return delta.total_seconds() <= limit_seconds
    return delta <= limit_seconds


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type 'A' event with the first later type 'B' event in the same
    session whose timestamp delta is no more than ``within`` seconds.

    Events are expected to contain at least:
      - ``type``: event type, with relevant values 'A' and 'B'
      - ``session_id``: session identifier
      - ``timestamp``: comparable timestamp value

    "Later" is determined by ``(timestamp, original_input_index)``. This allows
    events with equal timestamps to be ordered deterministically by their input
    order. Returned event dictionaries are the original dictionary objects.
    """
    if within < 0:
        return []

    b_events_by_session: dict[Any, list[tuple[Any, int, dict]]] = defaultdict(list)
    a_events: list[tuple[int, Any, Any, dict]] = []

    for index, event in enumerate(events):
        event_type = event.get("type")

        if event_type == "B":
            b_events_by_session[event["session_id"]].append(
                (event["timestamp"], index, event)
            )
        elif event_type == "A":
            a_events.append(
                (index, event["session_id"], event["timestamp"], event)
            )

    b_keys_by_session: dict[Any, list[tuple[Any, int]]] = {}

    for session_id, session_b_events in b_events_by_session.items():
        session_b_events.sort(key=lambda item: (item[0], item[1]))
        b_keys_by_session[session_id] = [
            (timestamp, index) for timestamp, index, _ in session_b_events
        ]

    correlated: list[tuple[dict, dict]] = []

    for a_index, session_id, a_timestamp, a_event in a_events:
        session_b_events = b_events_by_session.get(session_id)
        if not session_b_events:
            continue

        b_keys = b_keys_by_session[session_id]
        b_position = bisect_right(b_keys, (a_timestamp, a_index))

        if b_position >= len(session_b_events):
            continue

        b_timestamp, _, b_event = session_b_events[b_position]
        if _is_within(a_timestamp, b_timestamp, within):
            correlated.append((a_event, b_event))

    return correlated
