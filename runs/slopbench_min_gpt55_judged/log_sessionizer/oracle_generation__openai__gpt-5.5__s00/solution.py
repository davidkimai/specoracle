from __future__ import annotations

from typing import Any


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """Build user sessions from valid log events.

    Malformed events are skipped. A valid event is a dictionary with a string
    ``user_id`` and a non-bool integer ``timestamp``.
    """
    _validate_inputs(events, gap_seconds)

    sorted_events = _sorted_valid_events(events)
    sessions: list[dict] = []

    current_user: str | None = None
    current_start = 0
    current_end = 0
    current_count = 0

    for user_id, timestamp in sorted_events:
        if current_user is None:
            current_user = user_id
            current_start = timestamp
            current_end = timestamp
            current_count = 1
            continue

        starts_new_user = user_id != current_user
        starts_new_session = timestamp - current_end > gap_seconds

        if starts_new_user or starts_new_session:
            sessions.append(_session(current_user, current_start, current_end, current_count))
            current_user = user_id
            current_start = timestamp
            current_end = timestamp
            current_count = 1
            continue

        current_end = timestamp
        current_count += 1

    if current_user is not None:
        sessions.append(_session(current_user, current_start, current_end, current_count))

    return sessions


def _validate_inputs(events: list[dict], gap_seconds: int) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    if not _is_plain_int(gap_seconds):
        raise TypeError("gap_seconds must be an integer")

    if gap_seconds < 0:
        raise ValueError("gap_seconds must be non-negative")


def _sorted_valid_events(events: list[dict]) -> list[tuple[str, int]]:
    valid_events = []

    for event in events:
        normalized = _valid_event(event)
        if normalized is not None:
            valid_events.append(normalized)

    return sorted(valid_events, key=lambda item: (item[0], item[1]))


def _valid_event(event: Any) -> tuple[str, int] | None:
    if not isinstance(event, dict):
        return None

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    if not isinstance(user_id, str):
        return None

    if not _is_plain_int(timestamp):
        return None

    return user_id, timestamp


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _session(user_id: str, start: int, end: int, count: int) -> dict:
    return {
        "user_id": user_id,
        "start": start,
        "end": end,
        "count": count,
    }
