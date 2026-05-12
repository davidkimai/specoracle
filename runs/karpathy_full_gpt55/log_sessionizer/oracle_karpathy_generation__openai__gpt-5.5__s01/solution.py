def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    valid_events = []

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

    sessions = []
    current_user = None
    start = None
    end = None
    count = 0

    for user_id, timestamp in valid_events:
        if current_user != user_id or timestamp - end > gap_seconds:
            if current_user is not None:
                sessions.append({
                    "user_id": current_user,
                    "start": start,
                    "end": end,
                    "count": count,
                })

            current_user = user_id
            start = timestamp
            end = timestamp
            count = 1
        else:
            end = timestamp
            count += 1

    if current_user is not None:
        sessions.append({
            "user_id": current_user,
            "start": start,
            "end": end,
            "count": count,
        })

    return sessions
