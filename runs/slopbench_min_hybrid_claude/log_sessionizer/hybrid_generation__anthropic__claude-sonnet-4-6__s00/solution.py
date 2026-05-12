"""
log_sessionizer: group user events into sessions separated by time gaps.
"""

from __future__ import annotations

from itertools import groupby
from typing import Any


def _is_valid(event: Any) -> bool:
    """Return True when event has user_id and an integer timestamp."""
    if not isinstance(event, dict):
        return False
    if "user_id" not in event or "timestamp" not in event:
        return False
    if not isinstance(event["timestamp"], int):
        return False
    return True


def _sessions_for_user(user_id: str, timestamps: list[int], gap_seconds: int) -> list[dict]:
    """Build sessions for a single user from a sorted list of timestamps."""
    if not timestamps:
        return []

    sessions: list[dict] = []
    start = timestamps[0]
    end = timestamps[0]
    count = 1

    for ts in timestamps[1:]:
        if ts - end > gap_seconds:
            sessions.append({"user_id": user_id, "start": start, "end": end, "count": count})
            start = ts
            end = ts
            count = 1
        else:
            end = ts
            count += 1

    sessions.append({"user_id": user_id, "start": start, "end": end, "count": count})
    return sessions


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Group events into user sessions separated by gaps larger than gap_seconds.

    Parameters
    ----------
    events:
        Raw event dicts; each valid one must have 'user_id' and integer 'timestamp'.
    gap_seconds:
        Minimum gap (exclusive) that triggers a new session.

    Returns
    -------
    list[dict]
        Sessions sorted by user_id then start, each with keys:
        user_id, start, end, count.
    """
    valid = [e for e in events if _is_valid(e)]
    valid.sort(key=lambda e: (str(e["user_id"]), e["timestamp"]))

    sessions: list[dict] = []
    for user_id, group in groupby(valid, key=lambda e: str(e["user_id"])):
        timestamps = [e["timestamp"] for e in group]
        sessions.extend(_sessions_for_user(user_id, timestamps, gap_seconds))

    sessions.sort(key=lambda s: (s["user_id"], s["start"]))
    return sessions
