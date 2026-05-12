"""
log_sessionizer: group log events into user sessions based on time gaps.
"""

from __future__ import annotations


def _is_valid(event: dict) -> bool:
    """Return True if the event has a string-compatible user_id and integer timestamp."""
    if not isinstance(event, dict):
        return False
    if "user_id" not in event or "timestamp" not in event:
        return False
    if not isinstance(event["timestamp"], int):
        return False
    return True


def _normalize(event: dict) -> dict:
    """Return a cleaned event with user_id as str and timestamp as int."""
    return {"user_id": str(event["user_id"]), "timestamp": int(event["timestamp"])}


def _events_to_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """Convert a sorted list of single-user events into session dicts."""
    if not events:
        return []

    sessions = []
    start = events[0]["timestamp"]
    end = events[0]["timestamp"]
    count = 1
    user_id = events[0]["user_id"]

    for event in events[1:]:
        ts = event["timestamp"]
        if ts - end > gap_seconds:
            sessions.append({
                "user_id": user_id,
                "start": start,
                "end": end,
                "count": count,
                "duration": end - start,
            })
            start = ts
            count = 1
        else:
            count += 1
        end = ts

    sessions.append({
        "user_id": user_id,
        "start": start,
        "end": end,
        "count": count,
        "duration": end - start,
    })
    return sessions


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Build user sessions from a list of log events.

    Parameters
    ----------
    events:      Raw event dicts; each should have 'user_id' and integer 'timestamp'.
    gap_seconds: Minimum gap (exclusive) between events that triggers a new session.

    Returns
    -------
    List of session dicts sorted by user_id then start timestamp.
    Each session includes a 'duration' field equal to end - start.
    """
    valid = [_normalize(e) for e in events if _is_valid(e)]
    valid.sort(key=lambda e: (e["user_id"], e["timestamp"]))

    sessions: list[dict] = []

    # Group by user_id without itertools to keep dependencies obvious.
    i = 0
    while i < len(valid):
        user_id = valid[i]["user_id"]
        j = i
        while j < len(valid) and valid[j]["user_id"] == user_id:
            j += 1
        user_events = valid[i:j]
        sessions.extend(_events_to_sessions(user_events, gap_seconds))
        i = j

    return sessions
