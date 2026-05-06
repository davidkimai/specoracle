"""
event_correlator.py

Provides correlate_events() which pairs 'A' events with the first later 'B'
event in the same session_id within a given time window (in seconds).

Day 2: adds optional chain_types parameter to find ordered event-type chains.
"""

from __future__ import annotations

from collections import defaultdict


def correlate_events(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str] | None = None,
) -> list[tuple[dict, ...]]:
    """
    When chain_types is None (default):
        Pair each type-'A' event with the first later type-'B' event in the
        same session_id whose timestamp is within `within` seconds of the 'A'
        event.  Returns list[tuple[dict, dict]].

    When chain_types is provided:
        Find chains of events matching the ordered types in chain_types within
        the same session_id, where each adjacent step is within `within`
        seconds.  Returns list[tuple[dict, ...]] where each tuple has
        len(chain_types) elements.

    Parameters
    ----------
    events : list[dict]
        Each dict must have at least:
            - 'type'       : str
            - 'session_id' : hashable
            - 'timestamp'  : numeric (seconds since epoch, or any comparable number)
    within : int
        Maximum allowed time delta (seconds) between adjacent events.
    chain_types : list[str] | None
        When None, defaults to original ['A', 'B'] pairing behaviour.
        When provided, specifies the ordered sequence of event types to chain.

    Returns
    -------
    list[tuple[dict, ...]]
        Ordered list of event chains.  Each event appears at most once per
        position (first-come, first-served for earlier anchor events sorted
        by timestamp).
    """
    if chain_types is None:
        return _pair_ab(events, within=within)
    return _chain(events, within=within, chain_types=chain_types)


# ---------------------------------------------------------------------------
# Original A→B pairing logic (preserved exactly)
# ---------------------------------------------------------------------------

def _pair_ab(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    a_events: list[dict] = sorted(
        (e for e in events if e.get("type") == "A"),
        key=lambda e: e["timestamp"],
    )
    b_events: list[dict] = sorted(
        (e for e in events if e.get("type") == "B"),
        key=lambda e: e["timestamp"],
    )

    b_by_session: dict = defaultdict(list)
    for b in b_events:
        b_by_session[b["session_id"]].append(b)

    used_b: set[int] = set()

    pairs: list[tuple[dict, dict]] = []

    for a in a_events:
        session = a["session_id"]
        a_ts = a["timestamp"]

        candidates = b_by_session.get(session, [])
        for b in candidates:
            if id(b) in used_b:
                continue
            b_ts = b["timestamp"]
            if b_ts <= a_ts:
                continue
            if b_ts - a_ts <= within:
                used_b.add(id(b))
                pairs.append((a, b))
                break
            else:
                break

    return pairs


# ---------------------------------------------------------------------------
# Day 2: generalised chain logic
# ---------------------------------------------------------------------------

def _chain(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str],
) -> list[tuple[dict, ...]]:
    """
    Build chains of length len(chain_types) matching the ordered types,
    each adjacent pair in the same session within `within` seconds.

    Strategy: iterate over anchor events (first type), then greedily extend
    each chain one step at a time, consuming events so they are not reused.
    """
    if not chain_types:
        return []

    # Sort all events by timestamp once.
    sorted_events: list[dict] = sorted(events, key=lambda e: e["timestamp"])

    # Group events by (session_id, type) — preserving timestamp order.
    by_session_type: dict[tuple, list[dict]] = defaultdict(list)
    for e in sorted_events:
        key = (e["session_id"], e["type"])
        by_session_type[key].append(e)

    # We work through each anchor (first type) in timestamp order.
    anchors = list(by_session_type.get(
        # will be iterated properly below
        ("__sentinel__", chain_types[0]), []
    ))

    # Collect all events whose type matches chain_types[0] across all sessions.
    anchor_type = chain_types[0]
    anchor_events: list[dict] = sorted(
        (e for e in events if e.get("type") == anchor_type),
        key=lambda e: e["timestamp"],
    )

    used: set[int] = set()  # id() of consumed dicts
    chains: list[tuple[dict, ...]] = []

    for anchor in anchor_events:
        if id(anchor) in used:
            continue
        session = anchor["session_id"]
        # Try to extend the chain step by step.
        current_chain: list[dict] = [anchor]
        tentative_used: list[int] = [id(anchor)]
        success = True

        for step_idx in range(1, len(chain_types)):
            step_type = chain_types[step_idx]
            prev = current_chain[-1]
            prev_ts = prev["timestamp"]

            candidates = by_session_type.get((session, step_type), [])
            found = None
            for cand in candidates:
                if id(cand) in used or id(cand) in tentative_used:
                    continue
                cand_ts = cand["timestamp"]
                if cand_ts <= prev_ts:
                    continue
                if cand_ts - prev_ts <= within:
                    found = cand
                    break
                else:
                    # sorted, no later candidate can satisfy the window
                    break

            if found is None:
                success = False
                break
            current_chain.append(found)
            tentative_used.append(id(found))

        if success:
            for uid in tentative_used:
                used.add(uid)
            chains.append(tuple(current_chain))

    return chains
