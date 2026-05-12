from typing import Any


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    valid_events: list[tuple[str, int]] = []

    for event in events:
        if not isinstance(event, dict):
            continue

        user_id = event.get("user_id")
        timestamp = event.get("timestamp")

        if not isinstance(user_id, str):
            continue
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            continue

        valid_events.append((user_id, timestamp))

    valid_events.sort(key=lambda item: (item[0], item[1]))

    sessions: list[dict[str, Any]] = []

    current_user: str | None = None
    current_start: int | None = None
    current_end: int | None = None
    current_count = 0

    for user_id, timestamp in valid_events:
        if (
            current_user is None
            or user_id != current_user
            or current_end is None
            or timestamp - current_end > gap_seconds
        ):
            if current_user is not None:
                sessions.append(
                    {
                        "user_id": current_user,
                        "start": current_start,
                        "end": current_end,
                        "count": current_count,
                    }
                )

            current_user = user_id
            current_start = timestamp
            current_end = timestamp
            current_count = 1
        else:
            current_end = timestamp
            current_count += 1

    if current_user is not None:
        sessions.append(
            {
                "user_id": current_user,
                "start": current_start,
                "end": current_end,
                "count": current_count,
            }
        )

    return sessions
