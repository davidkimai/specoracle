from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Hashable


__all__ = ["correlate_events"]


@dataclass(frozen=True)
class EventRecord:
    index: int
    event: dict
    event_type: object
    session_id: Hashable
    timestamp: Real


BIndex = tuple[list[Real], list[EventRecord]]


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type 'A' event with the first later type 'B' event in the same
    session whose timestamp delta is no more than ``within`` seconds.

    Events must be dictionaries with keys: 'type', 'session_id', and
    'timestamp'. Timestamps must be finite real numbers. Returned pairs contain
    the original event dictionaries; they are not copied or mutated.
    """
    _validate_within(within)
    records = _validate_events(events)
    b_index_by_session = _build_b_index(records)

    pairs: list[tuple[dict, dict]] = []

    for record in records:
        if record.event_type != "A":
            continue

        b_index = b_index_by_session.get(record.session_id)
        match = _first_later_b(record, b_index, within)

        if match is not None:
            pairs.append((record.event, match.event))

    return pairs


def _validate_within(within: int) -> None:
    if isinstance(within, bool) or not isinstance(within, int):
        raise TypeError("within must be an integer number of seconds")

    if within < 0:
        raise ValueError("within must be non-negative")


def _validate_events(events: list[dict]) -> list[EventRecord]:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    return [_validate_event(event, index) for index, event in enumerate(events)]


def _validate_event(event: dict, index: int) -> EventRecord:
    if not isinstance(event, dict):
        raise TypeError(f"event at index {index} must be a dictionary")

    missing_keys = [key for key in ("type", "session_id", "timestamp") if key not in event]
    if missing_keys:
        names = ", ".join(repr(key) for key in missing_keys)
        raise ValueError(f"event at index {index} is missing required key(s): {names}")

    session_id = event["session_id"]
    _validate_session_id(session_id, index)

    return EventRecord(
        index=index,
        event=event,
        event_type=event["type"],
        session_id=session_id,
        timestamp=_validate_timestamp(event["timestamp"], index),
    )


def _validate_session_id(session_id: object, index: int) -> None:
    try:
        hash(session_id)
    except TypeError as exc:
        raise TypeError(f"event at index {index} has an unhashable session_id") from exc


def _validate_timestamp(timestamp: object, index: int) -> Real:
    if isinstance(timestamp, bool) or not isinstance(timestamp, Real):
        raise TypeError(f"event at index {index} has a non-numeric timestamp")

    if not isfinite(timestamp):
        raise ValueError(f"event at index {index} has a non-finite timestamp")

    return timestamp


def _build_b_index(records: list[EventRecord]) -> dict[Hashable, BIndex]:
    grouped: dict[Hashable, list[EventRecord]] = {}

    for record in records:
        if record.event_type != "B":
            continue
        grouped.setdefault(record.session_id, []).append(record)

    index: dict[Hashable, BIndex] = {}

    for session_id, session_records in grouped.items():
        ordered_records = sorted(session_records, key=lambda record: (record.timestamp, record.index))
        timestamps = [record.timestamp for record in ordered_records]
        index[session_id] = (timestamps, ordered_records)

    return index


def _first_later_b(record: EventRecord, b_index: BIndex | None, within: int) -> EventRecord | None:
    if b_index is None:
        return None

    timestamps, records = b_index
    position = bisect_right(timestamps, record.timestamp)

    if position == len(records):
        return None

    match = records[position]
    if match.timestamp - record.timestamp > within:
        return None

    return match
