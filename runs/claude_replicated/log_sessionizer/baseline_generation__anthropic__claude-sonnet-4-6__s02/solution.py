"""
log_sessionizer.py

Implements build_sessions for grouping log events into user sessions.
"""

from itertools import groupby


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build sessions from a list of log events.

    Parameters
    ----------
    events : list[dict]
        Each event should have 'user_id' and 'timestamp' keys.
        Malformed events (missing keys or non-integer timestamp) are skipped.
    gap_seconds : int
        If the gap between consecutive events for the same user exceeds this
        value, a new session is started.

    Returns
    -------
    list[dict]
        Sessions sorted by user_id then start time, each containing:
        {"user_id": str, "start": int, "end": int, "count": int}
    """
    valid_events = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if "user_id" not in event or "timestamp" not in event:
            continue
        try:
            timestamp = int(event["timestamp"])
        except (ValueError, TypeError):
            continue
        user_id = str(event["user_id"])
        valid_events.append((user_id, timestamp))

    # Sort by user_id then timestamp
    valid_events.sort(key=lambda x: (x[0], x[1]))

    sessions = []

    # Group by user_id
    for user_id, group in groupby(valid_events, key=lambda x: x[0]):
        user_events = [ts for _, ts in group]

        if not user_events:
            continue

        # Initialize first session
        session_start = user_events[0]
        session_end = user_events[0]
        session_count = 1

        for i in range(1, len(user_events)):
            current_ts = user_events[i]
            prev_ts = user_events[i - 1]

            if (current_ts - prev_ts) > gap_seconds:
                # Save current session and start a new one
                sessions.append({
                    "user_id": user_id,
                    "start": session_start,
                    "end": session_end,
                    "count": session_count,
                })
                session_start = current_ts
                session_end = current_ts
                session_count = 1
            else:
                session_end = current_ts
                session_count += 1

        # Save the last session for this user
        sessions.append({
            "user_id": user_id,
            "start": session_start,
            "end": session_end,
            "count": session_count,
        })

    # Sessions are already sorted by user_id then start because we sorted
    # valid_events and processed groups in order
    return sessions
