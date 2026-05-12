from typing import Any

__all__ = ["build_sessions"]


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """Build user sessions from valid log events.

    Malformed events are skipped. A valid event is a dictionary with a string
    ``user_id`` and an integer ``timestamp``.
    """
    _validate_inputs(events, gap_seconds)

    ordered_events = sorted(_valid_events(events), key=lambda item: (item[0], item[1]))

    sessions: list[dict] = []
    current_user: str | None = None
    start = 0
    end = 0
    count = 0

    for user_id, timestamp in ordered_events:
        if current_user is None:
            current_user = user_id
            start = timestamp
            end = timestamp
            count = 1
            continue

        starts_new_user = user_id != current_user
        starts_new_session = timestamp - end > gap_seconds

        if starts_new_user or starts_new_session:
            sessions.append(_session(current_user, start, end, count))
            current_user = user_id
            start = timestamp
            end = timestamp
            count = 1
            continue

        end = timestamp
        count += 1

    if current_user is not None:
        sessions.append(_session(current_user, start, end, count))

    return sessions


def _validate_inputs(events: list[dict], gap_seconds: int) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list")

    if isinstance(gap_seconds, bool) or not isinstance(gap_seconds, int):
        raise TypeError("gap_seconds must be an integer")

    if gap_seconds < 0:
        raise ValueError("gap_seconds must be non-negative")


def _valid_events(events: list[dict]) -> list[tuple[str, int]]:
    valid: list[tuple[str, int]] = []

    for event in events:
        parsed = _parse_event(event)
        if parsed is not None:
            valid.append(parsed)

    return valid


def _parse_event(event: Any) -> tuple[str, int] | None:
    if not isinstance(event, dict):
        return None

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    if not isinstance(user_id, str):
        return None

    if isinstance(timestamp, bool) or not isinstance(timestamp, int):
        return None

    return user_id, timestamp


def _session(user_id: str, start: int, end: int, count: int) -> dict:
    return {
        "user_id": user_id,
        "start": start,
        "end": end,
        "count": count,
    }
