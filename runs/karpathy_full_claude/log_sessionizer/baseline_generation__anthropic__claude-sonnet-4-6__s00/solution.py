"""
log_sessionizer.py

Provides build_sessions() for grouping log events into user sessions.
"""

from itertools import groupby


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build sessions from a list of log events.

    Parameters
    ----------
    events : list[dict]
        Each event should contain at least 'user_id' and 'timestamp' keys.
        Malformed events (missing keys or non-integer timestamp) are skipped.
    gap_seconds : int
        If the gap between consecutive events for a user exceeds this value,
        a new session is started.

    Returns
    -------
    list[dict]
        Sessions sorted by user_id then start timestamp.
        Each session dict has keys: user_id, start, end, count.
    """
    valid_events = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if "user_id" not in event or "timestamp" not in event:
            continue
        user_id = event["user_id"]
        timestamp = event["timestamp"]
        # Ensure timestamp is an integer (or can be treated as one)
        if not isinstance(timestamp, int):
            continue
        valid_events.append({"user_id": str(user_id), "timestamp": timestamp})

    # Sort by user_id then timestamp
    valid_events.sort(key=lambda e: (e["user_id"], e["timestamp"]))

    sessions = []

    for user_id, user_events_iter in groupby(valid_events, key=lambda e: e["user_id"]):
        user_events = list(user_events_iter)

        if not user_events:
            continue

        # Initialize first session
        first_ts = user_events[0]["timestamp"]
        current_start = first_ts
        current_end = first_ts
        current_count = 1

        for i in range(1, len(user_events)):
            ts = user_events[i]["timestamp"]
            gap = ts - current_end

            if gap > gap_seconds:
                # Save the current session and start a new one
                sessions.append({
                    "user_id": user_id,
                    "start": current_start,
                    "end": current_end,
                    "count": current_count,
                })
                current_start = ts
                current_end = ts
                current_count = 1
            else:
                current_end = ts
                current_count += 1

        # Append the last session for this user
        sessions.append({
            "user_id": user_id,
            "start": current_start,
            "end": current_end,
            "count": current_count,
        })

    # Sessions are already sorted by user_id then start because we processed
    # events in sorted order, but sort explicitly to guarantee the contract.
    sessions.sort(key=lambda s: (s["user_id"], s["start"]))

    return sessions
