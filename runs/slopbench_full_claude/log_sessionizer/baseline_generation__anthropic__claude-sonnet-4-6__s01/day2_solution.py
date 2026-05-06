from itertools import groupby


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    valid_events = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if "user_id" not in event or "timestamp" not in event:
            continue
        user_id = event["user_id"]
        timestamp = event["timestamp"]
        if not isinstance(timestamp, int):
            continue
        valid_events.append({"user_id": str(user_id), "timestamp": timestamp})

    valid_events.sort(key=lambda e: (e["user_id"], e["timestamp"]))

    sessions = []

    for user_id, user_events_iter in groupby(valid_events, key=lambda e: e["user_id"]):
        user_events = list(user_events_iter)

        if not user_events:
            continue

        session_start = user_events[0]["timestamp"]
        session_end = user_events[0]["timestamp"]
        session_count = 1

        for i in range(1, len(user_events)):
            current_ts = user_events[i]["timestamp"]
            prev_ts = user_events[i - 1]["timestamp"]

            if (current_ts - prev_ts) > gap_seconds:
                sessions.append({
                    "user_id": user_id,
                    "start": session_start,
                    "end": session_end,
                    "count": session_count,
                    "duration": session_end - session_start,
                })
                session_start = current_ts
                session_end = current_ts
                session_count = 1
            else:
                session_end = current_ts
                session_count += 1

        sessions.append({
            "user_id": user_id,
            "start": session_start,
            "end": session_end,
            "count": session_count,
            "duration": session_end - session_start,
        })

    sessions.sort(key=lambda s: (s["user_id"], s["start"]))

    return sessions
