"""
log_sessionizer.py

Builds user sessions from a flat list of timestamped events.
"""

from itertools import groupby


def _is_valid(event: dict) -> bool:
    """Return True only when the event has user_id and an integer timestamp."""
    if not isinstance(event, dict):
        return False
    if "user_id" not in event or "timestamp" not in event:
        return False
    if not isinstance(event["timestamp"], int):
        return False
    return True


def _events_to_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """Convert a sorted list of same-user events into session dicts."""
    if not events:
        return []

    sessions = []
    session_start = events[0]["timestamp"]
    session_end = events[0]["timestamp"]
    count = 1
    user_id = events[0]["user_id"]

    for event in events[1:]:
        ts = event["timestamp"]
        if ts - session_end > gap_seconds:
            sessions.append(
                {
                    "user_id": user_id,
                    "start": session_start,
                    "end": session_end,
                    "count": count,
                    "duration": session_end - session_start,
                }
            )
            session_start = ts
            count = 1
        else:
            count += 1
        session_end = ts

    sessions.append(
        {
            "user_id": user_id,
            "start": session_start,
            "end": session_end,
            "count": count,
            "duration": session_end - session_start,
        }
    )
    return sessions


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build sessions from a list of events.

    Parameters
    ----------
    events:      List of event dicts, each expected to have 'user_id' and 'timestamp'.
    gap_seconds: Inactivity threshold in seconds that triggers a new session.

    Returns
    -------
    List of session dicts sorted by (user_id, start).
    Each session contains: user_id, start, end, count, duration (end - start).
    """
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError("gap_seconds must be a non-negative integer")

    valid = [e for e in events if _is_valid(e)]
    valid.sort(key=lambda e: (str(e["user_id"]), e["timestamp"]))

    sessions = []
    for _, user_events in groupby(valid, key=lambda e: e["user_id"]):
        sessions.extend(_events_to_sessions(list(user_events), gap_seconds))

    sessions.sort(key=lambda s: (str(s["user_id"]), s["start"]))
    return sessions
