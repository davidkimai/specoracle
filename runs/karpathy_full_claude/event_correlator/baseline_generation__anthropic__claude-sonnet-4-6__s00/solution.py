"""
event_correlator.py

Correlates events by pairing each type 'A' event with the first later type 'B'
event in the same session_id where the time delta is within the specified seconds.
"""

from __future__ import annotations


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type 'A' event with the first later type 'B' event in the same
    session_id where the time delta is no more than *within* seconds.

    Parameters
    ----------
    events : list[dict]
        Each dict is expected to have at least:
            - 'type'       : str  ('A' or 'B', or other values which are ignored)
            - 'session_id' : hashable
            - 'timestamp'  : numeric (seconds since epoch, or any comparable number)
    within : int
        Maximum allowed time delta in seconds between the 'A' and 'B' events.

    Returns
    -------
    list[tuple[dict, dict]]
        Ordered list of (event_A, event_B) pairs.  Each 'A' event is paired at
        most once; each 'B' event is used at most once.
    """
    from collections import defaultdict

    # Group events by session_id
    sessions: dict = defaultdict(list)
    for event in events:
        sessions[event["session_id"]].append(event)

    # Sort each session's events by timestamp
    for session_id in sessions:
        sessions[session_id].sort(key=lambda e: e["timestamp"])

    pairs: list[tuple[dict, dict]] = []

    for session_id, session_events in sessions.items():
        # Collect A events and B events in order
        a_events = [e for e in session_events if e.get("type") == "A"]
        b_events = [e for e in session_events if e.get("type") == "B"]

        # Track which B events have already been matched
        used_b: set[int] = set()

        for a_event in a_events:
            a_time = a_event["timestamp"]
            # Find the first B event that:
            #   1. Has not been used yet
            #   2. Occurs strictly after the A event (timestamp > a_time)
            #   3. Is within the allowed time delta
            for idx, b_event in enumerate(b_events):
                if idx in used_b:
                    continue
                b_time = b_event["timestamp"]
                if b_time <= a_time:
                    continue
                if b_time - a_time <= within:
                    pairs.append((a_event, b_event))
                    used_b.add(idx)
                    break

    return pairs
