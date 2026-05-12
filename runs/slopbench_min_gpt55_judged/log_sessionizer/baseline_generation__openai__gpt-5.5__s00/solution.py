from __future__ import annotations

from typing import Any


def _is_valid_timestamp(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_valid_user_id(value: Any) -> bool:
    return isinstance(value, str)


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    valid_events: list[tuple[str, int]] = []

    for event in events:
        if not isinstance(event, dict):
            continue

        user_id = event.get("user_id")
        timestamp = event.get("timestamp")

        if not _is_valid_user_id(user_id):
            continue
        if not _is_valid_timestamp(timestamp):
            continue

        valid_events.append((user_id, timestamp))

    valid_events.sort(key=lambda item: (item[0], item[1]))

    sessions: list[dict] = []
    current_user: str | None = None
    session_start: int | None = None
    session_end: int | None = None
    session_count = 0

    def flush_session() -> None:
        nonlocal current_user, session_start, session_end, session_count
        if current_user is not None and session_start is not None and session_end is not None:
            sessions.append(
                {
                    "user_id": current_user,
                    "start": session_start,
                    "end": session_end,
                    "count": session_count,
                }
            )

    for user_id, timestamp in valid_events:
        if (
            current_user is None
            or user_id != current_user
            or session_end is None
            or timestamp - session_end > gap_seconds
        ):
            flush_session()
            current_user = user_id
            session_start = timestamp
            session_end = timestamp
            session_count = 1
        else:
            session_end = timestamp
            session_count += 1

    flush_session()
    return sessions
