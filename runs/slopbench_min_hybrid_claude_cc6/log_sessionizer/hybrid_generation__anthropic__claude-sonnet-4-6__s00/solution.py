"""
log_sessionizer: group log events into user sessions based on time gaps.
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


def _sessions_for_user(user_id: str, events: list[dict], gap_seconds: int) -> list[dict]:
    """Build sessions for a single user from their sorted events."""
    sessions = []
    start = end = count = None

    for event in events:
        ts = event["timestamp"]
        if start is None:
            start, end, count = ts, ts, 1
        elif ts - end > gap_seconds:
            sessions.append({"user_id": user_id, "start": start, "end": end, "count": count})
            start, end, count = ts, ts, 1
        else:
            end = ts
            count += 1

    if start is not None:
        sessions.append({"user_id": user_id, "start": start, "end": end, "count": count})

    return sessions


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Group log events into sessions per user.

    Parameters
    ----------
    events:      List of event dicts; each must have 'user_id' and integer 'timestamp'.
    gap_seconds: Maximum intra-session gap in seconds (inclusive).

    Returns
    -------
    List of session dicts sorted by user_id then start timestamp.
    """
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError(f"gap_seconds must be a non-negative integer, got {gap_seconds!r}")

    valid = [e for e in events if _is_valid(e)]
    valid.sort(key=lambda e: (str(e["user_id"]), e["timestamp"]))

    sessions = []
    for user_id, group in groupby(valid, key=lambda e: str(e["user_id"])):
        user_events = list(group)
        sessions.extend(_sessions_for_user(user_id, user_events, gap_seconds))

    sessions.sort(key=lambda s: (s["user_id"], s["start"]))
    return sessions
