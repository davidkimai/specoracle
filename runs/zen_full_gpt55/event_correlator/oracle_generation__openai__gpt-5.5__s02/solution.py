from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Hashable
from dataclasses import dataclass
from numbers import Real
from typing import DefaultDict

__all__ = ["correlate_events"]

_EVENT_TYPE_KEY = "type"
_SESSION_ID_KEY = "session_id"
_TIMESTAMP_KEY = "timestamp"


@dataclass(frozen=True)
class _IndexedEvent:
    index: int
    event: dict
    event_type: str
    session_id: Hashable
    timestamp: Real


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """Return pairs of A events and their first later B event in the same session.

    Events must be dictionaries with these keys:
    - "type": event type, with "A" and "B" being correlated
    - "session_id": a hashable session identifier
    - "timestamp": a finite numeric timestamp in seconds

    The returned dictionaries are the original event objects, not copies.
    """
    _validate_within(within)
    indexed_events = _validate_events(events)
    b_events_by_session = _collect_b_events(indexed_events)

    pairs: list[tuple[dict, dict]] = []

    for event in indexed_events:
        if event.event_type != "A":
            continue

        b_event = _first_later_b_event(
            event,
            b_events_by_session.get(event.session_id, []),
            within,
        )
        if b_event is not None:
            pairs.append((event.event, b_event.event))

    return pairs


def _validate_within(within: int) -> None:
    if isinstance(within, bool) or not isinstance(within, int):
        raise TypeError("within must be an integer number of seconds")
    if within < 0:
        raise ValueError("within must be non-negative")


def _validate_events(events: list[dict]) -> list[_IndexedEvent]:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    indexed_events: list[_IndexedEvent] = []

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"event at index {index} must be a dictionary")

        event_type = _required_value(event, _EVENT_TYPE_KEY, index)
        session_id = _required_value(event, _SESSION_ID_KEY, index)
        timestamp = _required_value(event, _TIMESTAMP_KEY, index)

        if not isinstance(event_type, str):
            raise TypeError(f"event at index {index} has a non-string type")

        _validate_session_id(session_id, index)
        timestamp = _validate_timestamp(timestamp, index)

        indexed_events.append(
            _IndexedEvent(
                index=index,
                event=event,
                event_type=event_type,
                session_id=session_id,
                timestamp=timestamp,
            )
        )

    return indexed_events


def _required_value(event: dict, key: str, index: int) -> object:
    if key not in event:
        raise KeyError(f"event at index {index} is missing required key {key!r}")
    return event[key]


def _validate_session_id(session_id: object, index: int) -> None:
    if not isinstance(session_id, Hashable):
        raise TypeError(f"event at index {index} has an unhashable session_id")


def _validate_timestamp(timestamp: object, index: int) -> Real:
    if isinstance(timestamp, bool) or not isinstance(timestamp, Real):
        raise TypeError(f"event at index {index} has a non-numeric timestamp")

    if isinstance(timestamp, float) and not math.isfinite(timestamp):
        raise ValueError(f"event at index {index} has a non-finite timestamp")

    return timestamp


def _collect_b_events(
    indexed_events: list[_IndexedEvent],
) -> dict[Hashable, list[_IndexedEvent]]:
    b_events_by_session: DefaultDict[Hashable, list[_IndexedEvent]] = defaultdict(list)

    for event in indexed_events:
        if event.event_type == "B":
            b_events_by_session[event.session_id].append(event)

    for b_events in b_events_by_session.values():
        b_events.sort(key=lambda event: (event.timestamp, event.index))

    return dict(b_events_by_session)


def _first_later_b_event(
    a_event: _IndexedEvent,
    b_events: list[_IndexedEvent],
    within: int,
) -> _IndexedEvent | None:
    for b_event in b_events:
        delta = b_event.timestamp - a_event.timestamp

        if delta <= 0:
            continue
        if delta > within:
            return None

        return b_event

    return None
