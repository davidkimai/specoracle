"""
event_correlator.py

Correlates events of type 'A' with the first later type 'B' event in the same
session within a given time window.
"""

from collections import defaultdict


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type 'A' event with the first later type 'B' event in the same
    session_id where the time delta (in seconds) is no more than `within`.

    Parameters
    ----------
    events : list[dict]
        Each dict must contain at least:
            - 'session_id': hashable identifier for the session
            - 'type': str, either 'A' or 'B' (others are ignored)
            - 'timestamp': numeric (int or float) representing seconds
    within : int
        Maximum allowed time difference in seconds between an 'A' event and its
        paired 'B' event.

    Returns
    -------
    list[tuple[dict, dict]]
        Each tuple is (a_event, b_event) where b_event is the first 'B' event
        that follows a_event in the same session within the time window.
        Each 'A' event appears at most once; each 'B' event may be used at most
        once (consumed by the first eligible 'A' that can claim it).
    """
    # Group events by session_id, separating A and B events
    session_a: dict[any, list[dict]] = defaultdict(list)
    session_b: dict[any, list[dict]] = defaultdict(list)

    for event in events:
        etype = event.get("type")
        sid = event.get("session_id")
        if etype == "A":
            session_a[sid].append(event)
        elif etype == "B":
            session_b[sid].append(event)

    # Sort each group by timestamp
    for sid in session_a:
        session_a[sid].sort(key=lambda e: e["timestamp"])
    for sid in session_b:
        session_b[sid].sort(key=lambda e: e["timestamp"])

    pairs: list[tuple[dict, dict]] = []

    for sid, a_events in session_a.items():
        b_events = session_b.get(sid, [])
        # Track which B events have been consumed
        b_used = [False] * len(b_events)

        for a_event in a_events:
            a_ts = a_event["timestamp"]
            # Find the first unused B event that is strictly later and within window
            for i, b_event in enumerate(b_events):
                if b_used[i]:
                    continue
                b_ts = b_event["timestamp"]
                delta = b_ts - a_ts
                if delta > 0 and delta <= within:
                    pairs.append((a_event, b_event))
                    b_used[i] = True
                    break
                # B events are sorted; if b_ts > a_ts + within we can stop early
                if b_ts > a_ts + within:
                    break

    return pairs
