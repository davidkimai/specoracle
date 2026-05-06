"""
event_correlator.py

Pairs each type-'A' event with the first later type-'B' event in the same
session that occurs within `within` seconds.
"""

from collections import defaultdict


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each 'A' event with the first later 'B' event in the same session_id
    whose timestamp is within `within` seconds of the 'A' event.

    Parameters
    ----------
    events : list[dict]
        Each dict must contain at least:
            - 'type'       : str  ('A' or 'B', others are ignored)
            - 'session_id' : hashable
            - 'timestamp'  : numeric (seconds)
    within : int
        Maximum allowed time delta (inclusive) in seconds between an 'A' and
        its paired 'B'.

    Returns
    -------
    list[tuple[dict, dict]]
        Ordered list of (A_event, B_event) pairs.  Each 'A' event appears at
        most once; each 'B' event may be reused if multiple 'A' events qualify,
        because the requirement is "first later B" per A.
    """
    if within < 0:
        raise ValueError(f"'within' must be non-negative, got {within!r}")

    _validate_events(events)

    # Sort once by timestamp so we can scan forward efficiently.
    sorted_events = sorted(events, key=lambda e: e["timestamp"])

    # Group B events by session for quick lookup.
    b_by_session: dict = defaultdict(list)
    for event in sorted_events:
        if event["type"] == "B":
            b_by_session[event["session_id"]].append(event)

    pairs: list[tuple[dict, dict]] = []

    for a_event in sorted_events:
        if a_event["type"] != "A":
            continue
        partner = _first_matching_b(a_event, b_by_session, within)
        if partner is not None:
            pairs.append((a_event, partner))

    return pairs


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_events(events: list[dict]) -> None:
    required_keys = {"type", "session_id", "timestamp"}
    for i, event in enumerate(events):
        missing = required_keys - event.keys()
        if missing:
            raise ValueError(
                f"Event at index {i} is missing required keys: {missing!r}"
            )


def _first_matching_b(
    a_event: dict,
    b_by_session: dict,
    within: int,
) -> dict | None:
    """Return the first B event in the same session that is later than *a_event*
    and within *within* seconds, or None if no such event exists."""
    session_bs = b_by_session.get(a_event["session_id"], [])
    a_time = a_event["timestamp"]

    for b_event in session_bs:
        b_time = b_event["timestamp"]
        if b_time > a_time and (b_time - a_time) <= within:
            return b_event
        # Because session_bs is sorted by timestamp, once we pass the window
        # there is no point continuing.
        if b_time > a_time + within:
            break

    return None
