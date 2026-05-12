def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_gap_seconds(gap_seconds: int) -> None:
    if not _is_plain_int(gap_seconds):
        raise TypeError("gap_seconds must be an integer")
    if gap_seconds < 0:
        raise ValueError("gap_seconds must be non-negative")


def _valid_event_tuple(event: object) -> tuple[str, int] | None:
    if not isinstance(event, dict):
        return None

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    if not isinstance(user_id, str):
        return None
    if not _is_plain_int(timestamp):
        return None

    return user_id, timestamp


def _valid_events(events: list[dict]) -> list[tuple[str, int]]:
    valid = []

    for event in events:
        event_tuple = _valid_event_tuple(event)
        if event_tuple is not None:
            valid.append(event_tuple)

    return sorted(valid, key=lambda item: (item[0], item[1]))


def _session_dict(user_id: str, start: int, end: int, count: int) -> dict:
    return {
        "user_id": user_id,
        "start": start,
        "end": end,
        "count": count,
    }


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    if not isinstance(events, list):
        raise TypeError("events must be a list")

    _validate_gap_seconds(gap_seconds)

    sorted_events = _valid_events(events)
    sessions = []

    current_user = None
    start = None
    end = None
    count = 0

    for user_id, timestamp in sorted_events:
        starts_first_session = current_user is None
        changes_user = user_id != current_user
        exceeds_gap = end is not None and timestamp - end > gap_seconds

        if starts_first_session or changes_user or exceeds_gap:
            if current_user is not None:
                sessions.append(_session_dict(current_user, start, end, count))

            current_user = user_id
            start = timestamp
            end = timestamp
            count = 1
            continue

        end = timestamp
        count += 1

    if current_user is not None:
        sessions.append(_session_dict(current_user, start, end, count))

    return sessions
