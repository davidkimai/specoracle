"""
event_correlator.py

Pairs each type-'A' event with the first later type-'B' event in the same
session that occurs within a given number of seconds.

Day 2: Adds chain_types parameter for chaining arbitrary ordered event types.
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


def _chain_in_session(
    session_events: list[dict], chain_types: list[str], within: int
) -> list[tuple]:
    """
    Find all chains of events matching chain_types in order within the session,
    where each adjacent pair is strictly increasing in timestamp and within the
    window.  Each chain is returned as a tuple of dicts.
    """
    if not chain_types:
        return []

    sorted_events = _sort_by_timestamp(session_events)

    # dp[i] is a list of in-progress chains that have matched chain_types[:i+1]
    # Each chain is stored as a list of event dicts.
    # We build chains greedily: for each event, try to extend existing partial chains.

    # chains_at_step[step] holds all partial chains of length (step+1)
    # that end with an event matching chain_types[step].
    chains_at_step: list[list[list[dict]]] = [[] for _ in chain_types]

    for event in sorted_events:
        etype = event["type"]
        # Walk steps in reverse so we don't use the same event twice in one pass
        for step in range(len(chain_types) - 1, -1, -1):
            if chain_types[step] != etype:
                continue
            if step == 0:
                # Start a new chain
                chains_at_step[0].append([event])
            else:
                # Try to extend chains from step-1
                prev_step_chains = chains_at_step[step - 1]
                for chain in prev_step_chains:
                    last_event = chain[-1]
                    if event["timestamp"] <= last_event["timestamp"]:
                        continue
                    delta = event["timestamp"] - last_event["timestamp"]
                    if delta <= within:
                        chains_at_step[step].append(chain + [event])

    return [tuple(chain) for chain in chains_at_step[len(chain_types) - 1]]


def correlate_events(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str] | None = None,
) -> list[tuple]:
    """
    Pair each type-'A' event with the first later type-'B' event in the same
    session_id where the time delta is no more than `within` seconds.

    When `chain_types` is provided, instead return chains of events matching
    the ordered types within the same session, with each adjacent step within
    the window.

    Parameters
    ----------
    events : list[dict]
        Each dict must contain 'session_id', 'type', and 'timestamp' (numeric).
    within : int
        Maximum allowed seconds between adjacent events (inclusive).
    chain_types : list[str] | None
        When provided, find ordered chains of these event types instead of the
        default A->B pairing.

    Returns
    -------
    list[tuple[dict, ...]]
        Ordered list of event tuples across all sessions.
        - Without chain_types: 2-tuples of (A-event, B-event).
        - With chain_types: N-tuples matching the requested chain.
    """
    if within < 0:
        raise ValueError(f"'within' must be non-negative, got {within!r}")

    session_groups = _group_by_session(events)

    results = []
    if chain_types is not None:
        for session_events in session_groups.values():
            results.extend(_chain_in_session(session_events, chain_types, within))
    else:
        for session_events in session_groups.values():
            results.extend(_pair_in_session(session_events, within))

    return results
