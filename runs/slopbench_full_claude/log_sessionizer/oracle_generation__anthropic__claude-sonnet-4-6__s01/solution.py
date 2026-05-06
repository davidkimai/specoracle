"""
log_sessionizer.py

Build user sessions from a flat list of timestamped events.
"""

from itertools import groupby


def _is_valid(event: dict) -> bool:
    """Return True when the event has a string-coercible user_id and an integer timestamp."""
    if not isinstance(event, dict):
        return False
    if "user_id" not in event or "timestamp" not in event:
        return False
    if not isinstance(event["timestamp"], int):
        return False
    return True


def _events_to_sessions(user_id: str, events: list[dict], gap_seconds: int) -> list[dict]:
    """Convert a sorted list of events for one user into session dicts."""
    sessions = []
    session_start = None
    session_end = None
    count = 0

    for event in events:
        ts = event["timestamp"]

        if session_start is None:
            session_start = ts
            session_end = ts
            count = 1
            continue

        if ts - session_end > gap_seconds:
            sessions.append({
                "user_id": user_id,
                "start": session_start,
                "end": session_end,
                "count": count,
            })
            session_start = ts
            session_end = ts
            count = 1
        else:
            session_end = ts
            count += 1

    if session_start is not None:
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
    events:      List of event dicts, each expected to have 'user_id' and 'timestamp'.
    gap_seconds: Inactivity gap (in seconds) that triggers a new session.

    Returns
    -------
    List of session dicts sorted by user_id then start timestamp.
    """
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError(f"gap_seconds must be a non-negative integer, got {gap_seconds!r}")

    valid_events = [e for e in events if _is_valid(e)]
    valid_events.sort(key=lambda e: (str(e["user_id"]), e["timestamp"]))

    sessions = []
    for user_id, group in groupby(valid_events, key=lambda e: str(e["user_id"])):
        user_events = list(group)
        sessions.extend(_events_to_sessions(user_id, user_events, gap_seconds))

    sessions.sort(key=lambda s: (s["user_id"], s["start"]))
    return sessions
