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


def _events_to_sessions(user_id: str, timestamps: list[int], gap_seconds: int) -> list[dict]:
    """Convert a sorted list of timestamps for one user into session dicts."""
    if not timestamps:
        return []

    sessions = []
    start = timestamps[0]
    end = timestamps[0]
    count = 1

    for ts in timestamps[1:]:
        if ts - end > gap_seconds:
            sessions.append({
                "user_id": user_id,
                "start": start,
                "end": end,
                "count": count,
                "duration": end - start,
            })
            start = ts
            end = ts
            count = 1
        else:
            end = ts
            count += 1

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
    Build sessions from a list of events.

    Parameters
    ----------
    events:      List of dicts, each expected to have 'user_id' and 'timestamp'.
    gap_seconds: Inactivity gap (strictly greater than) that starts a new session.

    Returns
    -------
    List of session dicts sorted by user_id then start time.
    Each session contains: user_id, start, end, count, duration (end - start).
    """
    if not isinstance(gap_seconds, int):
        raise TypeError(f"gap_seconds must be an int, got {type(gap_seconds).__name__}")
    if gap_seconds < 0:
        raise ValueError(f"gap_seconds must be non-negative, got {gap_seconds}")

    valid_events = [e for e in events if _is_valid(e)]

    valid_events.sort(key=lambda e: (str(e["user_id"]), e["timestamp"]))

    sessions = []
    for user_id, group in groupby(valid_events, key=lambda e: str(e["user_id"])):
        timestamps = [e["timestamp"] for e in group]
        sessions.extend(_events_to_sessions(user_id, timestamps, gap_seconds))

    sessions.sort(key=lambda s: (s["user_id"], s["start"]))
    return sessions
