from typing import Any


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build per-user sessions from event records.

    A valid event is a dictionary with:
      - "user_id": str
      - "timestamp": int, excluding bool

    Malformed events are skipped. Valid events are sorted by user_id and
    timestamp. For each user, a new session starts when the gap from the
    previous event is greater than gap_seconds.
    """
    valid_events: list[tuple[str, int]] = []

    for event in events:
        if not isinstance(event, dict):
            continue

        user_id: Any = event.get("user_id")
        timestamp: Any = event.get("timestamp")

        if not isinstance(user_id, str):
            continue
        if isinstance(timestamp, bool) or not isinstance(timestamp, int):
            continue

        valid_events.append((user_id, timestamp))

    valid_events.sort(key=lambda item: (item[0], item[1]))

    sessions: list[dict] = []

    current_user: str | None = None
    session_start: int | None = None
    session_end: int | None = None
    session_count = 0
    previous_timestamp: int | None = None

    for user_id, timestamp in valid_events:
        starts_new_user = current_user != user_id
        starts_new_session = (
            previous_timestamp is not None
            and timestamp - previous_timestamp > gap_seconds
        )

        if starts_new_user or starts_new_session:
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

        previous_timestamp = timestamp

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
