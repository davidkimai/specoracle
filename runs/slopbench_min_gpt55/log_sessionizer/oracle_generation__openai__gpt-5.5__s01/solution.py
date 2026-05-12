from typing import Any


def _validate_gap_seconds(gap_seconds: int) -> None:
    if isinstance(gap_seconds, bool) or not isinstance(gap_seconds, int):
        raise TypeError("gap_seconds must be an integer")
    if gap_seconds < 0:
        raise ValueError("gap_seconds must be non-negative")


def _valid_event(event: Any) -> tuple[str, int] | None:
    if not isinstance(event, dict):
        return None

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    if not isinstance(user_id, str):
        return None
    if isinstance(timestamp, bool) or not isinstance(timestamp, int):
        return None

    return user_id, timestamp


def _sorted_valid_events(events: list[dict]) -> list[tuple[str, int]]:
    valid_events = []

    for event in events:
        valid_event = _valid_event(event)
        if valid_event is not None:
            valid_events.append(valid_event)

    return sorted(valid_events, key=lambda item: (item[0], item[1]))


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    if not isinstance(events, list):
        raise TypeError("events must be a list")

    _validate_gap_seconds(gap_seconds)

    sessions: list[dict] = []
    current_session: dict | None = None
    previous_user_id: str | None = None
    previous_timestamp: int | None = None

    for user_id, timestamp in _sorted_valid_events(events):
        starts_new_user = user_id != previous_user_id
        starts_new_session = (
            previous_timestamp is None
            or timestamp - previous_timestamp > gap_seconds
        )

        if starts_new_user or starts_new_session:
            current_session = {
                "user_id": user_id,
                "start": timestamp,
                "end": timestamp,
                "count": 1,
            }
            sessions.append(current_session)
        else:
            current_session["end"] = timestamp
            current_session["count"] += 1

        previous_user_id = user_id
        previous_timestamp = timestamp

    return sessions
