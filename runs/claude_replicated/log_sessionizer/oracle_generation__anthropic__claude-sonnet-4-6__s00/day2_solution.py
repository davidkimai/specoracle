"""
log_sessionizer: group user events into sessions based on time gaps.
"""

from itertools import groupby


def _is_valid(event: dict) -> bool:
    """Return True if event has user_id and an integer timestamp."""
    if not isinstance(event, dict):
        return False
    if "user_id" not in event or "timestamp" not in event:
        return False
    if not isinstance(event["timestamp"], int):
        return False
    return True


def _sessions_for_user(timestamps: list[int], gap_seconds: int) -> list[dict]:
    """Build session records for a single user's sorted timestamps."""
    if not timestamps:
        return []

    sessions = []
    start = timestamps[0]
    end = timestamps[0]
    count = 1

    for ts in timestamps[1:]:
        if ts - end > gap_seconds:
            sessions.append({"start": start, "end": end, "count": count, "duration": end - start})
            start = ts
            count = 1
        else:
            count += 1
        end = ts

    sessions.append({"start": start, "end": end, "count": count, "duration": end - start})
    return sessions


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Group events into sessions per user.

    Parameters
    ----------
    events:      list of event dicts, each needing 'user_id' and 'timestamp'.
    gap_seconds: maximum intra-session gap; larger gaps start a new session.

    Returns
    -------
    List of session dicts sorted by user_id then start timestamp.
    Each session includes a 'duration' field equal to end - start.
    """
    if not isinstance(gap_seconds, int):
        raise TypeError(f"gap_seconds must be an int, got {type(gap_seconds).__name__}")

    valid = [e for e in events if _is_valid(e)]
    valid.sort(key=lambda e: (str(e["user_id"]), e["timestamp"]))

    result = []
    for user_id, group in groupby(valid, key=lambda e: e["user_id"]):
        timestamps = [e["timestamp"] for e in group]
        for session in _sessions_for_user(timestamps, gap_seconds):
            result.append({"user_id": str(user_id), **session})

    return result
