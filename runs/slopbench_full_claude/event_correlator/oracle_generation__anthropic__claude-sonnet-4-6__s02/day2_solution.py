"""
event_correlator.py

Correlate events of type 'A' with the first later type 'B' event in the same
session within a given time window.

Day 2: Added chain_types parameter to support ordered multi-type event chains.
"""

from collections import defaultdict


def correlate_events(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str] | None = None,
) -> list[tuple[dict, ...]]:
    """
    Pair each type-'A' event with the first later type-'B' event sharing the
    same session_id whose timestamp is within `within` seconds.

    When chain_types is provided, return chains of events matching the ordered
    types within the same session, with each adjacent step within the window.

    Parameters
    ----------
    events:
        Each dict must contain at least 'session_id', 'type', and 'timestamp'
        (numeric seconds).
    within:
        Maximum allowed time delta (inclusive) in seconds between adjacent
        events in a pair or chain.
    chain_types:
        When provided, a list of event types to chain in order (e.g.
        ['A', 'B', 'C']). Returns tuples of matching events where each
        consecutive pair is within `within` seconds and in the same session.
        When None, the original A->B pairing behavior is used.

    Returns
    -------
    A list of tuples. In the original mode (chain_types=None), each tuple is
    (a_event, b_event). In chain mode, each tuple contains one event per type
    in chain_types order.
    """
    if within < 0:
        raise ValueError(f"'within' must be non-negative, got {within!r}")

    _validate_events(events)

    if chain_types is not None:
        return _correlate_chain(events, within=within, chain_types=chain_types)

    # Original A->B pairing behavior
    b_by_session = _group_b_events(events)
    pairs: list[tuple[dict, ...]] = []

    for a_event in events:
        if a_event["type"] != "A":
            continue
        match = _find_first_matching_b(a_event, b_by_session, within)
        if match is not None:
            pairs.append((a_event, match))

    return pairs


# ---------------------------------------------------------------------------
# Chain helpers (Day 2)
# ---------------------------------------------------------------------------

def _correlate_chain(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str],
) -> list[tuple[dict, ...]]:
    """
    Return chains of events matching chain_types in order within the same
    session, with each adjacent step within `within` seconds.

    For each event matching chain_types[0], we greedily find the first event
    matching chain_types[1] that is later and within the window, then the
    first matching chain_types[2] after that, and so on.
    """
    if not chain_types:
        return []

    # Group events by session_id and type, sorted by timestamp
    by_session_type: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for event in events:
        by_session_type[event["session_id"]][event["type"]].append(event)

    for session_id in by_session_type:
        for typ in by_session_type[session_id]:
            by_session_type[session_id][typ].sort(key=lambda e: e["timestamp"])

    chains: list[tuple[dict, ...]] = []

    # Iterate over events in original order to find starting events
    for start_event in events:
        if start_event["type"] != chain_types[0]:
            continue

        session_id = start_event["session_id"]
        chain: list[dict] = [start_event]
        current = start_event

        for next_type in chain_types[1:]:
            candidates = by_session_type[session_id].get(next_type, [])
            match = _find_first_after(current, candidates, within)
            if match is None:
                break
            chain.append(match)
            current = match
        else:
            # All types matched
            if len(chain) == len(chain_types):
                chains.append(tuple(chain))

    return chains


def _find_first_after(
    prev_event: dict,
    candidates: list[dict],
    within: int,
) -> dict | None:
    """
    Return the first event in candidates that occurs strictly after prev_event
    and within `within` seconds of it, or None.
    Candidates must be sorted by timestamp.
    """
    prev_time = prev_event["timestamp"]
    for event in candidates:
        t = event["timestamp"]
        if t > prev_time and (t - prev_time) <= within:
            return event
    return None


# ---------------------------------------------------------------------------
# Original helpers
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
