"""
event_correlator.py

Correlates events of type 'A' with the first later type 'B' event in the same
session within a given time window.

Day 2: Adds chain_types parameter to find ordered chains of event types.
"""

from collections import defaultdict
from typing import Optional


def correlate_events(
    events: list[dict],
    *,
    within: int,
    chain_types: Optional[list[str]] = None,
) -> list[tuple[dict, ...]]:
    """
    When chain_types is None (default):
        Pair each type 'A' event with the first later type 'B' event in the same
        session_id where the time delta (in seconds) is no more than `within`.

    When chain_types is provided:
        Find chains of events matching the ordered types in chain_types within
        the same session, where each adjacent pair of events in the chain is
        within `within` seconds of each other. Each event may be consumed at
        most once (greedy, left-to-right).

    Parameters
    ----------
    events : list[dict]
        Each dict must contain at least:
            - 'session_id': hashable identifier for the session
            - 'type': str
            - 'timestamp': numeric (int or float) representing seconds
    within : int
        Maximum allowed time difference in seconds between adjacent events in a
        pair or chain.
    chain_types : list[str] | None
        When provided, an ordered list of event types forming the desired chain.
        Must have at least 2 elements.

    Returns
    -------
    list[tuple[dict, ...]]
        When chain_types is None: list of 2-tuples (a_event, b_event).
        When chain_types is provided: list of N-tuples where N == len(chain_types).
    """
    if chain_types is not None:
        return _correlate_chain(events, within=within, chain_types=chain_types)
    return _correlate_ab(events, within=within)


def _correlate_ab(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """Original A->B pairing logic."""
    session_a: dict = defaultdict(list)
    session_b: dict = defaultdict(list)

    for event in events:
        etype = event.get("type")
        sid = event.get("session_id")
        if etype == "A":
            session_a[sid].append(event)
        elif etype == "B":
            session_b[sid].append(event)

    for sid in session_a:
        session_a[sid].sort(key=lambda e: e["timestamp"])
    for sid in session_b:
        session_b[sid].sort(key=lambda e: e["timestamp"])

    pairs: list[tuple[dict, dict]] = []

    for sid, a_events in session_a.items():
        b_events = session_b.get(sid, [])
        b_used = [False] * len(b_events)

        for a_event in a_events:
            a_ts = a_event["timestamp"]
            for i, b_event in enumerate(b_events):
                if b_used[i]:
                    continue
                b_ts = b_event["timestamp"]
                delta = b_ts - a_ts
                if delta > 0 and delta <= within:
                    pairs.append((a_event, b_event))
                    b_used[i] = True
                    break
                if b_ts > a_ts + within:
                    break

    return pairs


def _correlate_chain(
    events: list[dict], *, within: int, chain_types: list[str]
) -> list[tuple[dict, ...]]:
    """
    Find ordered chains of events matching chain_types within the same session,
    each adjacent step within `within` seconds. Greedy, left-to-right consumption.
    """
    if len(chain_types) < 2:
        raise ValueError("chain_types must contain at least 2 type labels")

    # Group events by session_id, then by type, sorted by timestamp
    # Structure: session_events[sid][type] = sorted list of events
    session_events: dict = defaultdict(lambda: defaultdict(list))

    relevant_types = set(chain_types)
    for event in events:
        etype = event.get("type")
        sid = event.get("session_id")
        if etype in relevant_types:
            session_events[sid][etype].append(event)

    for sid in session_events:
        for etype in session_events[sid]:
            session_events[sid][etype].sort(key=lambda e: e["timestamp"])

    chains: list[tuple[dict, ...]] = []

    # Collect all sessions that have at least the first type
    all_sids = set(session_events.keys())

    for sid in all_sids:
        type_lists = session_events[sid]

        # Check that all required types exist in this session
        if not all(t in type_lists for t in chain_types):
            continue

        # used[type] tracks which indices in type_lists[type] are consumed
        used: dict[str, list[bool]] = {
            t: [False] * len(type_lists[t]) for t in chain_types
        }

        # Iterate over each candidate starting event (first type in chain)
        first_type = chain_types[0]
        for start_idx, start_event in enumerate(type_lists[first_type]):
            if used[first_type][start_idx]:
                continue

            # Try to build a chain greedily
            chain: list[dict] = [start_event]
            chain_indices: list[tuple[str, int]] = [(first_type, start_idx)]
            success = True

            for step in range(1, len(chain_types)):
                prev_event = chain[-1]
                prev_ts = prev_event["timestamp"]
                curr_type = chain_types[step]
                curr_list = type_lists[curr_type]
                curr_used = used[curr_type]

                found = False
                for j, candidate in enumerate(curr_list):
                    if curr_used[j]:
                        continue
                    c_ts = candidate["timestamp"]
                    delta = c_ts - prev_ts
                    if delta > 0 and delta <= within:
                        chain.append(candidate)
                        chain_indices.append((curr_type, j))
                        found = True
                        break
                    if c_ts > prev_ts + within:
                        break

                if not found:
                    success = False
                    break

            if success:
                # Mark all events in this chain as consumed
                for t, idx in chain_indices:
                    used[t][idx] = True
                chains.append(tuple(chain))

    return chains
