from __future__ import annotations

from typing import Any


def _is_integer_timestamp(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    valid_events: list[tuple[str, int]] = []

    for event in events:
        if not isinstance(event, dict):
            continue

        if "user_id" not in event or "timestamp" not in event:
            continue

        user_id = event["user_id"]
        timestamp = event["timestamp"]

        if not isinstance(user_id, str):
            continue

        if not _is_integer_timestamp(timestamp):
            continue

        valid_events.append((user_id, timestamp))

    valid_events.sort(key=lambda item: (item[0], item[1]))

    sessions: list[dict] = []

    current_user: str | None = None
    session_start: int | None = None
    session_end: int | None = None
    session_count = 0

    for user_id, timestamp in valid_events:
        if (
            current_user is None
            or user_id != current_user
            or session_end is None
            or timestamp - session_end > gap_seconds
        ):
            if current_user is not None:
                sessions.append(
                    {
                        "user_id": current_user,
                        "start": session_start,
                        "end": session_end,
                        "count": session_count,
                    }
                )

            current_user = user_id
            session_start = timestamp
            session_end = timestamp
            session_count = 1
        else:
            session_end = timestamp
            session_count += 1

    if current_user is not None:
        sessions.append(
            {
                "user_id": current_user,
                "start": session_start,
                "end": session_end,
                "count": session_count,
            }
        )

    return sessions
