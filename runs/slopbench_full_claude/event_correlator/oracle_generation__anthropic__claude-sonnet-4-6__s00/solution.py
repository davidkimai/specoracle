"""
event_correlator.py

Pairs each type-'A' event with the first later type-'B' event in the same
session that occurs within a given number of seconds.
"""

from collections import defaultdict


def _validate_event(event: dict) -> None:
    for field in ("session_id", "type", "timestamp"):
        if field not in event:
            raise ValueError(f"Event is missing required field: {field!r}")


def _group_by_session(events: list[dict]) -> dict:
    groups: dict = defaultdict(list)
    for event in events:
        _validate_event(event)
        groups[event["session_id"]].append(event)
    return groups


def _sort_by_timestamp(events: list[dict]) -> list[dict]:
    return sorted(events, key=lambda e: e["timestamp"])


def _pair_in_session(session_events: list[dict], within: int) -> list[tuple[dict, dict]]:
    sorted_events = _sort_by_timestamp(session_events)
    a_events = [e for e in sorted_events if e["type"] == "A"]
    b_events = [e for e in sorted_events if e["type"] == "B"]

    pairs = []
    used_b = set()

    for a in a_events:
        for idx, b in enumerate(b_events):
            if idx in used_b:
                continue
            if b["timestamp"] <= a["timestamp"]:
                continue
            delta = b["timestamp"] - a["timestamp"]
            if delta <= within:
                pairs.append((a, b))
                used_b.add(idx)
                break

    return pairs


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type-'A' event with the first later type-'B' event in the same
    session_id where the time delta is no more than `within` seconds.

    Parameters
    ----------
    events : list[dict]
        Each dict must contain 'session_id', 'type', and 'timestamp' (numeric).
    within : int
        Maximum allowed seconds between the 'A' and 'B' event (inclusive).

    Returns
    -------
    list[tuple[dict, dict]]
        Ordered list of (A-event, B-event) pairs across all sessions.
    """
    if within < 0:
        raise ValueError(f"'within' must be non-negative, got {within!r}")

    session_groups = _group_by_session(events)

    pairs = []
    for session_events in session_groups.values():
        pairs.extend(_pair_in_session(session_events, within))

    return pairs
