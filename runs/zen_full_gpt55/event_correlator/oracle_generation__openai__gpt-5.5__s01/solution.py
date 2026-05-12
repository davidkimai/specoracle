from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict
from collections.abc import Hashable
from math import isfinite
from numbers import Real
from typing import Any, NamedTuple


_REQUIRED_KEYS = ("type", "session_id", "timestamp")


class _PreparedEvent(NamedTuple):
    index: int
    event: dict
    event_type: Any
    session_id: Hashable
    timestamp: Real


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    window = _validate_within(within)
    prepared_events = _prepare_events(events)

    b_events_by_session = _build_b_index(prepared_events)

    pairs: list[tuple[dict, dict]] = []
    for prepared in prepared_events:
        if prepared.event_type != "A":
            continue

        b_times, b_events = b_events_by_session.get(prepared.session_id, ((), ()))
        b_position = bisect_right(b_times, prepared.timestamp)
        if b_position == len(b_times):
            continue

        b_time = b_times[b_position]
        if b_time - prepared.timestamp <= window:
            pairs.append((prepared.event, b_events[b_position]))

    return pairs


def _validate_within(within: int) -> int:
    if isinstance(within, bool) or not isinstance(within, int):
        raise TypeError("within must be an integer number of seconds")
    if within < 0:
        raise ValueError("within must be non-negative")
    return within


def _prepare_events(events: list[dict]) -> list[_PreparedEvent]:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    prepared_events: list[_PreparedEvent] = []
    for index, event in enumerate(events):
        prepared_events.append(_prepare_event(index, event))

    return prepared_events


def _prepare_event(index: int, event: dict) -> _PreparedEvent:
    if not isinstance(event, dict):
        raise TypeError(f"events[{index}] must be a dictionary")

    for key in _REQUIRED_KEYS:
        if key not in event:
            raise KeyError(f"events[{index}] is missing required key {key!r}")

    session_id = event["session_id"]
    if not isinstance(session_id, Hashable):
        raise TypeError(f"events[{index}]['session_id'] must be hashable")

    timestamp = event["timestamp"]
    if isinstance(timestamp, bool) or not isinstance(timestamp, Real):
        raise TypeError(f"events[{index}]['timestamp'] must be a real number")
    if not isfinite(timestamp):
        raise ValueError(f"events[{index}]['timestamp'] must be finite")

    return _PreparedEvent(
        index=index,
        event=event,
        event_type=event["type"],
        session_id=session_id,
        timestamp=timestamp,
    )


def _build_b_index(
    prepared_events: list[_PreparedEvent],
) -> dict[Hashable, tuple[list[Real], list[dict]]]:
    grouped: dict[Hashable, list[_PreparedEvent]] = defaultdict(list)

    for prepared in prepared_events:
        if prepared.event_type == "B":
            grouped[prepared.session_id].append(prepared)

    indexed: dict[Hashable, tuple[list[Real], list[dict]]] = {}
    for session_id, session_events in grouped.items():
        ordered = sorted(session_events, key=lambda item: (item.timestamp, item.index))
        indexed[session_id] = (
            [item.timestamp for item in ordered],
            [item.event for item in ordered],
        )

    return indexed
