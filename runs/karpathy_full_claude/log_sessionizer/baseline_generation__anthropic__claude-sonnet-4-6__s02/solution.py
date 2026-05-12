"""
log_sessionizer.py

Provides build_sessions() to group log events into user sessions based on
time gaps.
"""

from __future__ import annotations


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Group log events into sessions per user.

    Parameters
    ----------
    events : list[dict]
        Each element should contain at least ``user_id`` (str-convertible) and
        ``timestamp`` (integer-convertible).  Malformed entries are silently
        skipped.
    gap_seconds : int
        If the time gap between two consecutive events for the same user
        exceeds this value, a new session is started.

    Returns
    -------
    list[dict]
        Sessions sorted by ``user_id`` then ``start``, each with keys:
        ``user_id``, ``start``, ``end``, ``count``.
    """
    # --- validate / normalise events ----------------------------------------
    valid: list[tuple[str, int]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if "user_id" not in event or "timestamp" not in event:
            continue
        try:
            uid = str(event["user_id"])
            ts = int(event["timestamp"])
        except (TypeError, ValueError):
            continue
        valid.append((uid, ts))

    # --- sort by (user_id, timestamp) ----------------------------------------
    valid.sort(key=lambda x: (x[0], x[1]))

    # --- build sessions -------------------------------------------------------
    sessions: list[dict] = []

    if not valid:
        return sessions

    current_user: str = valid[0][0]
    session_start: int = valid[0][1]
    session_end: int = valid[0][1]
    session_count: int = 1

    for uid, ts in valid[1:]:
        if uid == current_user and (ts - session_end) <= gap_seconds:
            # extend current session
            session_end = ts
            session_count += 1
        else:
            # flush current session
            sessions.append(
                {
                    "user_id": current_user,
                    "start": session_start,
                    "end": session_end,
                    "count": session_count,
                }
            )
            # start new session
            current_user = uid
            session_start = ts
            session_end = ts
            session_count = 1

    # flush the last session
    sessions.append(
        {
            "user_id": current_user,
            "start": session_start,
            "end": session_end,
            "count": session_count,
        }
    )

    # sessions are already sorted by (user_id, start) due to the initial sort
    return sessions
