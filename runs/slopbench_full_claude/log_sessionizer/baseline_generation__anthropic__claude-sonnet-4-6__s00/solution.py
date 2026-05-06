"""
log_sessionizer.py

Implements build_sessions for grouping log events into user sessions.
"""

from itertools import groupby


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build sessions from a list of events.

    Parameters
    ----------
    events : list[dict]
        Each event should have 'user_id' (str) and 'timestamp' (int).
        Malformed events (missing keys or non-integer timestamps) are skipped.
    gap_seconds : int
        Maximum gap in seconds between consecutive events in the same session.
        If the gap exceeds this value, a new session is started.

    Returns
    -------
    list[dict]
        Sessions sorted by user_id then start time, each containing:
        - user_id (str)
        - start (int)
        - end (int)
        - count (int)
    """
    # Filter and validate events
    valid_events = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if "user_id" not in event or "timestamp" not in event:
            continue
        user_id = event["user_id"]
        timestamp = event["timestamp"]
        # user_id must be convertible to str (non-None), timestamp must be int
        if user_id is None:
            continue
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            continue
        valid_events.append({"user_id": str(user_id), "timestamp": timestamp})

    # Sort by user_id then timestamp
    valid_events.sort(key=lambda e: (e["user_id"], e["timestamp"]))

    sessions = []

    # Group by user_id
    for user_id, user_events_iter in groupby(valid_events, key=lambda e: e["user_id"]):
        user_events = list(user_events_iter)

        # Build sessions for this user
        session_start = None
        session_end = None
        session_count = 0
        prev_timestamp = None

        for event in user_events:
            ts = event["timestamp"]

            if prev_timestamp is None:
                # First event for this user
                session_start = ts
                session_end = ts
                session_count = 1
            else:
                gap = ts - prev_timestamp
                if gap > gap_seconds:
                    # Save current session and start a new one
                    sessions.append({
                        "user_id": user_id,
                        "start": session_start,
                        "end": session_end,
                        "count": session_count,
                    })
                    session_start = ts
                    session_end = ts
                    session_count = 1
                else:
                    # Extend current session
                    session_end = ts
                    session_count += 1

            prev_timestamp = ts

        # Don't forget the last session for this user
        if session_start is not None:
            sessions.append({
                "user_id": user_id,
                "start": session_start,
                "end": session_end,
                "count": session_count,
            })

    # Sessions are already sorted by user_id then start (due to pre-sorting)
    return sessions
