"""
event_correlator.py

Pairs each type-'A' event with the first later type-'B' event in the same
session_id whose timestamp falls within `within` seconds of the 'A' event.

Assumptions:
- Each event dict has at least: 'type' (str), 'session_id' (hashable),
  'timestamp' (numeric, seconds since epoch or any consistent numeric unit).
- "First later" means the smallest timestamp strictly greater than the 'A'
  timestamp, within the allowed delta.
- Each 'A' event is paired at most once; each 'B' event is consumed at most
  once (greedy, earliest-A-first).
- Events may arrive in any order; we sort internally.
"""

from collections import defaultdict


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    # Group events by session_id
    sessions: dict = defaultdict(lambda: {"A": [], "B": []})
    for event in events:
        t = event.get("type")
        if t in ("A", "B"):
            sessions[event["session_id"]][t].append(event)

    pairs: list[tuple[dict, dict]] = []

    for session_events in sessions.values():
        a_events = sorted(session_events["A"], key=lambda e: e["timestamp"])
        b_events = sorted(session_events["B"], key=lambda e: e["timestamp"])

        used_b = [False] * len(b_events)

        for a in a_events:
            a_ts = a["timestamp"]
            # Find first unused B with timestamp in (a_ts, a_ts + within]
            for i, b in enumerate(b_events):
                if used_b[i]:
                    continue
                b_ts = b["timestamp"]
                if b_ts > a_ts and (b_ts - a_ts) <= within:
                    pairs.append((a, b))
                    used_b[i] = True
                    break

    return pairs
