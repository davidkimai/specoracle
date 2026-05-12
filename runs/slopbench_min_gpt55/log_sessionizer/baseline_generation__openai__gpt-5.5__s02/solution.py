"""Log sessionization module."""

from __future__ import annotations


def _is_valid_timestamp(value: object) -> bool:
    """Return True when value is an integer timestamp, excluding booleans."""
    return isinstance(value, int) and not isinstance(value, bool)


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build user sessions from log events.

    A valid event is a dictionary with:
      - user_id: str
      - timestamp: int (bool is not accepted)

    Events are sorted by user_id then timestamp. For each user, a new session is
    started when the gap from the previous event is greater than gap_seconds.
    Malformed events are skipped.
    """
    valid_events: list[tuple[str, int]] = []

    for event in events:
        if not isinstance(event, dict):
            continue

        user_id = event.get("user_id")
        timestamp = event.get("timestamp")

        if not isinstance(user_id, str):
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
