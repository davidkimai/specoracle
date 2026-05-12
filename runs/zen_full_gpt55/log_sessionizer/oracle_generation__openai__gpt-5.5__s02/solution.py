def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_event(event: object) -> tuple[str, int] | None:
    if not isinstance(event, dict):
        return None

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    if not isinstance(user_id, str):
        return None
    if not _is_plain_int(timestamp):
        return None

    return user_id, timestamp


def _validate_inputs(events: list[dict], gap_seconds: int) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list")
    if not _is_plain_int(gap_seconds):
        raise TypeError("gap_seconds must be an integer")


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    _validate_inputs(events, gap_seconds)

    valid_events = []
    for event in events:
        parsed_event = _valid_event(event)
        if parsed_event is not None:
            valid_events.append(parsed_event)

    valid_events.sort(key=lambda item: (item[0], item[1]))

    sessions = []
    current_user = None
    current_start = None
    current_end = None
    current_count = 0

    for user_id, timestamp in valid_events:
        if current_user != user_id:
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
            continue

        if timestamp - current_end > gap_seconds:
            sessions.append(
                {
                    "user_id": current_user,
                    "start": current_start,
                    "end": current_end,
                    "count": current_count,
                }
            )
            current_start = timestamp
            current_end = timestamp
            current_count = 1
            continue

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
