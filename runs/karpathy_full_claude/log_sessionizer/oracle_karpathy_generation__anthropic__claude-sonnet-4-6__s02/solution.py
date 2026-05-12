def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    valid = []
    for e in events:
        try:
            user_id = e["user_id"]
            timestamp = int(e["timestamp"])
            valid.append((str(user_id), timestamp))
        except (KeyError, TypeError, ValueError):
            continue

    valid.sort()

    sessions = []
    i = 0
    while i < len(valid):
        user, ts = valid[i]
        start = ts
        end = ts
        count = 1
        j = i + 1
        while j < len(valid) and valid[j][0] == user and valid[j][1] - end <= gap_seconds:
            end = valid[j][1]
            count += 1
            j += 1
        sessions.append({"user_id": user, "start": start, "end": end, "count": count})
        i = j

    return sessions
