"""
log_sessionizer.py

Implements build_sessions for grouping user events into sessions based on
time gaps.
"""

from itertools import groupby


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build sessions from a list of events.

    Parameters
    ----------
    events : list[dict]
        Each event should contain 'user_id' and 'timestamp' keys.
        Malformed events (missing keys or non-integer timestamp) are skipped.
    gap_seconds : int
        Maximum allowed gap (in seconds) between consecutive events within the
        same session. A gap strictly greater than this value starts a new session.

    Returns
    -------
    list[dict]
        List of session dicts with keys: user_id, start, end, duration, count.
        Sorted by user_id then start.
    """
    valid_events = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if "user_id" not in event or "timestamp" not in event:
            continue
        try:
            ts = int(event["timestamp"])
        except (TypeError, ValueError):
            continue
        user_id = event["user_id"]
        if user_id is None:
            continue
        valid_events.append({"user_id": str(user_id), "timestamp": ts})

    # Sort by user_id then timestamp
    valid_events.sort(key=lambda e: (e["user_id"], e["timestamp"]))

    sessions = []

    for user_id, user_events_iter in groupby(valid_events, key=lambda e: e["user_id"]):
        user_events = list(user_events_iter)

        # Start the first session
        session_start = user_events[0]["timestamp"]
        session_end = user_events[0]["timestamp"]
        session_count = 1

        for i in range(1, len(user_events)):
            current_ts = user_events[i]["timestamp"]
            prev_ts = user_events[i - 1]["timestamp"]

            if current_ts - prev_ts > gap_seconds:
                # Close current session and start a new one
                sessions.append({
                    "user_id": user_id,
                    "start": session_start,
                    "end": session_end,
                    "duration": session_end - session_start,
                    "count": session_count,
                })
                session_start = current_ts
                session_end = current_ts
                session_count = 1
            else:
                session_end = current_ts
                session_count += 1

        # Close the last session for this user
        sessions.append({
            "user_id": user_id,
            "start": session_start,
            "end": session_end,
            "duration": session_end - session_start,
            "count": session_count,
        })

    # Already sorted by user_id then start due to sorted input and groupby
    return sessions
