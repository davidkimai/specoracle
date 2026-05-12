"""
log_sessionizer.py

Build user sessions from a flat list of timestamped events.
"""

from itertools import groupby


def _is_valid(event: dict) -> bool:
    """Return True if the event has user_id and an integer timestamp."""
    if not isinstance(event, dict):
        return False
    if "user_id" not in event or "timestamp" not in event:
        return False
    if not isinstance(event["timestamp"], int):
        return False
    return True


def _sessions_for_user(user_id: str, timestamps: list[int], gap_seconds: int) -> list[dict]:
    """Convert a sorted list of timestamps for one user into session dicts."""
    sessions = []
    session_start = timestamps[0]
    session_end = timestamps[0]
    count = 1

    for ts in timestamps[1:]:
        if ts - session_end > gap_seconds:
            sessions.append({
                "user_id": user_id,
                "start": session_start,
                "end": session_end,
                "count": count,
            })
            session_start = ts
            count = 1
        else:
            count += 1
        session_end = ts

    sessions.append({
        "user_id": user_id,
        "start": session_start,
        "end": session_end,
        "count": count,
    })
    return sessions


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build sessions from a list of events.

    Parameters
    ----------
    events:
        Each event should be a dict with at least 'user_id' and 'timestamp' (int).
        Malformed events are silently skipped.
    gap_seconds:
        A new session begins when the gap between consecutive events exceeds
        this value (strictly greater than).

    Returns
    -------
    List of session dicts sorted by user_id then start time.
    """
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError("gap_seconds must be a non-negative integer")

    valid = [e for e in events if _is_valid(e)]
    valid.sort(key=lambda e: (str(e["user_id"]), e["timestamp"]))

    sessions = []
    for user_id, group in groupby(valid, key=lambda e: str(e["user_id"])):
        timestamps = [e["timestamp"] for e in group]
        sessions.extend(_sessions_for_user(user_id, timestamps, gap_seconds))

    sessions.sort(key=lambda s: (s["user_id"], s["start"]))
    return sessions
