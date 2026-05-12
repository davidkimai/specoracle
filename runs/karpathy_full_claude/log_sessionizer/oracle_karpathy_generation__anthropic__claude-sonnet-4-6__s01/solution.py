from itertools import groupby

def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    valid = []
    for e in events:
        if not isinstance(e, dict):
            continue
        if 'user_id' not in e or 'timestamp' not in e:
            continue
        try:
            ts = int(e['timestamp'])
        except (TypeError, ValueError):
            continue
        valid.append((str(e['user_id']), ts))

    valid.sort(key=lambda x: (x[0], x[1]))

    sessions = []
    for user_id, group in groupby(valid, key=lambda x: x[0]):
        timestamps = [ts for _, ts in group]
        start = timestamps[0]
        end = timestamps[0]
        count = 1
        for ts in timestamps[1:]:
            if ts - end > gap_seconds:
                sessions.append({"user_id": user_id, "start": start, "end": end, "count": count})
                start = ts
                end = ts
                count = 1
            else:
                end = ts
                count += 1
        sessions.append({"user_id": user_id, "start": start, "end": end, "count": count})

    return sessions
