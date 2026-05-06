"""
event_correlator.py

Provides correlate_events(), which pairs type-'A' events with the first
later type-'B' event in the same session whose timestamp is within the
specified number of seconds.
"""

from __future__ import annotations


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type-'A' event with the first later type-'B' event that:
      - shares the same session_id
      - has a timestamp strictly greater than the 'A' event's timestamp
      - has a time delta (b.timestamp - a.timestamp) <= within seconds

    Each 'B' event is consumed by at most one 'A' event (first-come, first-served
    based on the order of 'A' events processed).

    Parameters
    ----------
    events : list[dict]
        Each dict is expected to have at minimum:
            - 'type'       : str  ('A' or 'B')
            - 'session_id' : hashable
            - 'timestamp'  : numeric (seconds since epoch or any numeric unit)
    within : int
        Maximum allowed time delta in seconds between the 'A' and 'B' events.

    Returns
    -------
    list[tuple[dict, dict]]
        Ordered list of (a_event, b_event) pairs in the order the 'A' events
        appear in the input list.
    """
    # Group B events by session_id, sorted by timestamp ascending so we can
    # find the *first* later B for each A efficiently.
    from collections import defaultdict

    # We'll keep track of which B events have already been used.
    # Store B events per session as a list of (timestamp, index_in_original, dict)
    # sorted by timestamp so we can iterate in order.
    b_by_session: dict = defaultdict(list)

    for event in events:
        if event.get("type") == "B":
            session = event.get("session_id")
            b_by_session[session].append(event)

    # Sort each session's B events by timestamp
    for session in b_by_session:
        b_by_session[session].sort(key=lambda e: e["timestamp"])

    # Track which B events have been consumed; use id() as a proxy for identity
    used_b_ids: set[int] = set()

    pairs: list[tuple[dict, dict]] = []

    for a_event in events:
        if a_event.get("type") != "A":
            continue

        session = a_event.get("session_id")
        a_ts = a_event["timestamp"]

        candidates = b_by_session.get(session, [])

        for b_event in candidates:
            if id(b_event) in used_b_ids:
                continue
            b_ts = b_event["timestamp"]
            delta = b_ts - a_ts
            if delta > 0 and delta <= within:
                pairs.append((a_event, b_event))
                used_b_ids.add(id(b_event))
                break  # first valid B found; stop looking

    return pairs
