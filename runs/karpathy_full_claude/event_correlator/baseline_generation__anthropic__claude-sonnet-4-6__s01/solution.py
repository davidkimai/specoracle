"""
event_correlator.py

Correlates events of type 'A' with the first later event of type 'B'
within the same session_id and within a specified time window.
"""

from collections import defaultdict


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type 'A' event with the first later type 'B' event in the same
    session_id where the time delta is no more than `within` seconds.

    Parameters
    ----------
    events : list[dict]
        Each dict must contain at least:
            - 'type'       : str  ('A' or 'B' or other)
            - 'session_id' : hashable
            - 'timestamp'  : numeric (seconds since epoch or any comparable number)
    within : int
        Maximum allowed time difference in seconds between the 'A' event and
        its paired 'B' event.

    Returns
    -------
    list[tuple[dict, dict]]
        Ordered list of (a_event, b_event) pairs.  Each 'A' event is paired
        at most once; each 'B' event is paired at most once (first eligible
        match wins for both sides).
    """
    # Group events by session_id, then separate into A and B lists per session.
    session_a: dict = defaultdict(list)
    session_b: dict = defaultdict(list)

    for event in events:
        etype = event.get("type")
        sid = event.get("session_id")
        if etype == "A":
            session_a[sid].append(event)
        elif etype == "B":
            session_b[sid].append(event)

    # Sort each group by timestamp so we can do an efficient linear scan.
    for sid in session_a:
        session_a[sid].sort(key=lambda e: e["timestamp"])
    for sid in session_b:
        session_b[sid].sort(key=lambda e: e["timestamp"])

    pairs: list[tuple[dict, dict]] = []

    for sid, a_events in session_a.items():
        b_events = session_b.get(sid, [])
        if not b_events:
            continue

        # Two-pointer approach:
        # For each A event (in timestamp order), find the first unused B event
        # that is strictly later and within `within` seconds.
        b_index = 0          # Points to the first candidate B event
        used_b: set = set()  # Indices of B events already consumed

        for a_event in a_events:
            a_ts = a_event["timestamp"]

            # Advance b_index past any B events that are not strictly later
            # than this A event.
            while b_index < len(b_events) and b_events[b_index]["timestamp"] <= a_ts:
                b_index += 1

            # Scan forward for the first unused B event within the window.
            for j in range(b_index, len(b_events)):
                if j in used_b:
                    continue
                b_ts = b_events[j]["timestamp"]
                if b_ts - a_ts > within:
                    # B events are sorted; no later one can be closer.
                    break
                # Found a valid pair.
                used_b.add(j)
                pairs.append((a_event, b_events[j]))
                break

    # Sort the result by the A event's timestamp for deterministic output.
    pairs.sort(key=lambda p: p[0]["timestamp"])

    return pairs
