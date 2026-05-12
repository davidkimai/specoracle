def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_inputs(events: list[dict], gap_seconds: int) -> None:
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    if not _is_integer(gap_seconds):
        raise TypeError("gap_seconds must be an integer")

    if gap_seconds < 0:
        raise ValueError("gap_seconds must be non-negative")


def _valid_event_pairs(events: list[dict]) -> list[tuple[str, int]]:
    pairs: list[tuple[str, int]] = []

    for event in events:
        if not isinstance(event, dict):
            continue

        user_id = event.get("user_id")
        timestamp = event.get("timestamp")

        if not isinstance(user_id, str):
            continue

        if not _is_integer(timestamp):
            continue

        pairs.append((user_id, timestamp))

    return pairs


def _session_dict(user_id: str, start: int, end: int, count: int) -> dict:
    return {
        "user_id": user_id,
        "start": start,
        "end": end,
        "count": count,
    }


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    _validate_inputs(events, gap_seconds)

    event_pairs = sorted(_valid_event_pairs(events), key=lambda item: (item[0], item[1]))
    sessions: list[dict] = []

    current_user: str | None = None
    start = 0
    end = 0
    count = 0

    for user_id, timestamp in event_pairs:
        if current_user is None:
            current_user = user_id
            start = timestamp
            end = timestamp
            count = 1
            continue

        same_session = user_id == current_user and timestamp - end <= gap_seconds
        if same_session:
            end = timestamp
            count += 1
            continue

        sessions.append(_session_dict(current_user, start, end, count))
        current_user = user_id
        start = timestamp
        end = timestamp
        count = 1

    if current_user is not None:
        sessions.append(_session_dict(current_user, start, end, count))

    return sessions
