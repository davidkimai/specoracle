"""
event_correlator.py

Provides correlate_events() which pairs 'A' events with the first later 'B'
event in the same session_id within a given time window (in seconds).
"""

from __future__ import annotations


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type-'A' event with the first later type-'B' event in the same
    session_id whose timestamp is within `within` seconds of the 'A' event.

    Parameters
    ----------
    events : list[dict]
        Each dict must have at least:
            - 'type'       : str  ('A' or 'B', others are ignored)
            - 'session_id' : hashable
            - 'timestamp'  : numeric (seconds since epoch, or any comparable number)
    within : int
        Maximum allowed time delta (seconds) between the 'A' and 'B' event.

    Returns
    -------
    list[tuple[dict, dict]]
        Ordered list of (A_event, B_event) pairs.  Each 'A' event appears at
        most once; each 'B' event is used at most once (first-come, first-served
        for 'A' events sorted by timestamp).
    """
    # Separate and sort A and B events by timestamp
    a_events: list[dict] = sorted(
        (e for e in events if e.get("type") == "A"),
        key=lambda e: e["timestamp"],
    )
    b_events: list[dict] = sorted(
        (e for e in events if e.get("type") == "B"),
        key=lambda e: e["timestamp"],
    )

    # Group B events by session_id for efficient lookup
    # Within each session the list is already sorted by timestamp (inherited
    # from the sort above).
    from collections import defaultdict

    b_by_session: dict = defaultdict(list)
    for b in b_events:
        b_by_session[b["session_id"]].append(b)

    # Track which B events have already been consumed
    used_b: set[int] = set()  # use id() to identify dict instances

    pairs: list[tuple[dict, dict]] = []

    for a in a_events:
        session = a["session_id"]
        a_ts = a["timestamp"]

        candidates = b_by_session.get(session, [])
        for b in candidates:
            if id(b) in used_b:
                continue
            b_ts = b["timestamp"]
            if b_ts <= a_ts:
                # B must be *later* than A
                continue
            if b_ts - a_ts <= within:
                # Found the first eligible B for this A
                used_b.add(id(b))
                pairs.append((a, b))
                break
            else:
                # Since candidates are sorted by timestamp, no later B can
                # satisfy the window either.
                break

    return pairs
