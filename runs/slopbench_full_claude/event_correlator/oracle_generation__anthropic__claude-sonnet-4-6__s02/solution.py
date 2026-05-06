"""
event_correlator.py

Correlate events of type 'A' with the first later type 'B' event in the same
session within a given time window.
"""

from collections import defaultdict


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type-'A' event with the first later type-'B' event sharing the
    same session_id whose timestamp is within `within` seconds.

    Parameters
    ----------
    events:
        Each dict must contain at least 'session_id', 'type', and 'timestamp'
        (numeric seconds).
    within:
        Maximum allowed time delta (inclusive) in seconds between an 'A' event
        and its matched 'B' event.

    Returns
    -------
    A list of (a_event, b_event) tuples in the order the 'A' events appear.
    """
    if within < 0:
        raise ValueError(f"'within' must be non-negative, got {within!r}")

    _validate_events(events)

    b_by_session = _group_b_events(events)
    pairs = []

    for a_event in events:
        if a_event["type"] != "A":
            continue
        match = _find_first_matching_b(a_event, b_by_session, within)
        if match is not None:
            pairs.append((a_event, match))

    return pairs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_events(events: list[dict]) -> None:
    required_keys = {"session_id", "type", "timestamp"}
    for i, event in enumerate(events):
        missing = required_keys - event.keys()
        if missing:
            raise ValueError(
                f"Event at index {i} is missing required keys: {missing!r}"
            )


def _group_b_events(events: list[dict]) -> dict[str, list[dict]]:
    """Return type-'B' events grouped by session_id, sorted by timestamp."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        if event["type"] == "B":
            groups[event["session_id"]].append(event)
    for session_id in groups:
        groups[session_id].sort(key=lambda e: e["timestamp"])
    return groups


def _find_first_matching_b(
    a_event: dict,
    b_by_session: dict[str, list[dict]],
    within: int,
) -> dict | None:
    """
    Return the first 'B' event in the same session that occurs after the 'A'
    event and within `within` seconds, or None if no such event exists.
    """
    session_id = a_event["session_id"]
    a_time = a_event["timestamp"]
    candidates = b_by_session.get(session_id, [])

    for b_event in candidates:
        b_time = b_event["timestamp"]
        if b_time > a_time and (b_time - a_time) <= within:
            return b_event
        # Because candidates are sorted, once b_time exceeds the window we
        # can stop only if b_time > a_time + within.  We cannot break early
        # on b_time <= a_time because later entries might still qualify.

    return None
