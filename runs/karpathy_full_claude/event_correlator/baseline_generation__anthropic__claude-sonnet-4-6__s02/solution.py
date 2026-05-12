"""
event_correlator.py

Provides correlate_events() which pairs type-'A' events with the first
subsequent type-'B' event in the same session within a given time window.
"""

from __future__ import annotations


def correlate_events(
    events: list[dict],
    *,
    within: int,
) -> list[tuple[dict, dict]]:
    """Pair each type-'A' event with the first later type-'B' event that:
      - shares the same ``session_id``
      - occurs no more than ``within`` seconds after the 'A' event

    Each 'B' event may only be used once (consumed by the first matching 'A').

    Parameters
    ----------
    events:
        Sequence of event dicts.  Each dict is expected to contain at least:
          - ``"type"``       : str  ('A' or 'B', or other – others are ignored)
          - ``"session_id"`` : hashable
          - ``"timestamp"``  : numeric (seconds, e.g. Unix epoch)
    within:
        Maximum allowed difference in seconds (inclusive) between the
        'A' timestamp and the 'B' timestamp.

    Returns
    -------
    list[tuple[dict, dict]]
        Ordered list of (a_event, b_event) pairs in the order the 'A' events
        appear in the input.
    """
    from collections import defaultdict

    # Separate and index B events by session_id, sorted by timestamp
    b_by_session: dict = defaultdict(list)
    for event in events:
        if event.get("type") == "B":
            b_by_session[event["session_id"]].append(event)

    # Sort each session's B events by timestamp so we can scan efficiently
    for session_id in b_by_session:
        b_by_session[session_id].sort(key=lambda e: e["timestamp"])

    # Track which B events have already been consumed (by object id)
    used_b_ids: set[int] = set()

    pairs: list[tuple[dict, dict]] = []

    for a_event in events:
        if a_event.get("type") != "A":
            continue

        session_id = a_event["session_id"]
        a_ts = a_event["timestamp"]
        candidates = b_by_session.get(session_id, [])

        for b_event in candidates:
            b_ts = b_event["timestamp"]
            # Must be strictly later (b_ts > a_ts) and within the window
            if b_ts <= a_ts:
                continue
            if b_ts - a_ts > within:
                # Since candidates are sorted, no later ones can qualify
                break
            if id(b_event) in used_b_ids:
                continue
            # Found the first valid, unused B event
            used_b_ids.add(id(b_event))
            pairs.append((a_event, b_event))
            break

    return pairs
