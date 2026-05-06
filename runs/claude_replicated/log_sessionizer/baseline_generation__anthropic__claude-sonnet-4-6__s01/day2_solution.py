"""
log_sessionizer.py

Implements build_sessions to group log events into user sessions based on
a configurable time gap threshold.
"""

from itertools import groupby


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Group events into sessions per user.

    Parameters
    ----------
    events : list[dict]
        Raw event dicts; each should have 'user_id' and 'timestamp'.
    gap_seconds : int
        If the gap between two consecutive events for a user exceeds this
        value, a new session is started.

    Returns
    -------
    list[dict]
        Sessions sorted by user_id then start, each containing:
        {"user_id": str, "start": int, "end": int, "count": int, "duration": int}
        where duration = end - start.
    """
    # --- 1. Filter valid events ---
    valid = []
    for event in events:
        if not isinstance(event, dict):
            continue
        user_id = event.get("user_id")
        timestamp = event.get("timestamp")
        if user_id is None or timestamp is None:
            continue
        # user_id must be convertible to str (non-None already covers that)
        # timestamp must be an integer (bool is a subclass of int; exclude it)
        if isinstance(timestamp, bool) or not isinstance(timestamp, int):
            continue
        valid.append({"user_id": str(user_id), "timestamp": timestamp})

    # --- 2. Sort by user_id, then timestamp ---
    valid.sort(key=lambda e: (e["user_id"], e["timestamp"]))

    # --- 3. Build sessions ---
    sessions = []

    for user_id, user_events_iter in groupby(valid, key=lambda e: e["user_id"]):
        user_events = list(user_events_iter)

        # Initialise first session
        first_ts = user_events[0]["timestamp"]
        session_start = first_ts
        session_end = first_ts
        session_count = 1

        for event in user_events[1:]:
            ts = event["timestamp"]
            if ts - session_end > gap_seconds:
                # Close current session and start a new one
                sessions.append({
                    "user_id": user_id,
                    "start": session_start,
                    "end": session_end,
                    "count": session_count,
                    "duration": session_end - session_start,
                })
                session_start = ts
                session_end = ts
                session_count = 1
            else:
                session_end = ts
                session_count += 1

        # Close the last session for this user
        sessions.append({
            "user_id": user_id,
            "start": session_start,
            "end": session_end,
            "count": session_count,
            "duration": session_end - session_start,
        })

    # Sessions are already ordered by user_id then start due to the sort above
    return sessions
