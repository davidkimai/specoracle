"""
event_correlator.py

Provides correlate_events(), which pairs type-'A' events with the first
later type-'B' event in the same session whose timestamp is within the
specified number of seconds.

Day 2 extension: optional chain_types parameter that, when provided, finds
ordered chains of events matching the specified type sequence within the same
session, with each adjacent step within the window.
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
        Pair each type-'A' event with the first later type-'B' event that:
          - shares the same session_id
          - has a timestamp strictly greater than the 'A' event's timestamp
          - has a time delta (b.timestamp - a.timestamp) <= within seconds

        Each 'B' event is consumed by at most one 'A' event (first-come,
        first-served based on the order of 'A' events processed).

        Returns list[tuple[dict, dict]].

    When chain_types is provided:
        Find all chains of events matching the ordered types in chain_types
        within the same session, where each adjacent pair of events satisfies:
          - later event's timestamp > earlier event's timestamp
          - time delta between adjacent events <= within seconds

        Each event may be consumed by at most one chain (first-come,
        first-served based on the order the first event in the chain appears
        in the input list).

        Returns list[tuple[dict, ...]], where each tuple has len(chain_types)
        elements.

    Parameters
    ----------
    events : list[dict]
        Each dict is expected to have at minimum:
            - 'type'       : str
            - 'session_id' : hashable
            - 'timestamp'  : numeric (seconds since epoch or any numeric unit)
    within : int
        Maximum allowed time delta in seconds between adjacent events.
    chain_types : list[str] | None
        When provided, the ordered sequence of event types to chain.

    Returns
    -------
    list[tuple[dict, ...]]
        Ordered list of event tuples.
    """
    if chain_types is None:
        return _correlate_ab(events, within=within)
    else:
        return _correlate_chain(events, within=within, chain_types=chain_types)


# ---------------------------------------------------------------------------
# Original A→B logic (preserved exactly)
# ---------------------------------------------------------------------------

def _correlate_ab(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    b_by_session: dict = defaultdict(list)

    for event in events:
        if event.get("type") == "B":
            session = event.get("session_id")
            b_by_session[session].append(event)

    for session in b_by_session:
        b_by_session[session].sort(key=lambda e: e["timestamp"])

    used_b_ids: set[int] = set()
    pairs: list[tuple[dict, dict]] = []

    for a_event in events:
        if a_event.get("type") != "A":
            continue

        session = a_event.get("session_id")
        a_ts = a_event["timestamp"]

        candidates = b_by_session.get(session, [])

        for b_event in candidates:
            if id(b_event) in used_b_ids:
                continue
            b_ts = b_event["timestamp"]
            delta = b_ts - a_ts
            if delta > 0 and delta <= within:
                pairs.append((a_event, b_event))
                used_b_ids.add(id(b_event))
                break

    return pairs


# ---------------------------------------------------------------------------
# Day 2: generic chain logic
# ---------------------------------------------------------------------------

def _correlate_chain(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str],
) -> list[tuple[dict, ...]]:
    """
    Build chains of events matching chain_types in order, within the same
    session, with each adjacent step within the time window.

    Strategy:
      - Group events by (session_id, type), sorted by timestamp.
      - For each event of chain_types[0] (in input order), greedily find the
        first unused event of chain_types[1] that is within the window, then
        the first unused event of chain_types[2] after that, etc.
      - Events are consumed (used) as chains are built.
    """
    if not chain_types:
        return []

    # Group events by session and type, preserving original order then sorting
    # by timestamp so we can find the "first later" event efficiently.
    # Structure: by_session_type[session][type] = list of events sorted by timestamp
    by_session_type: dict = defaultdict(lambda: defaultdict(list))

    for event in events:
        t = event.get("type")
        s = event.get("session_id")
        by_session_type[s][t].append(event)

    for s in by_session_type:
        for t in by_session_type[s]:
            by_session_type[s][t].sort(key=lambda e: e["timestamp"])

    used_ids: set[int] = set()
    chains: list[tuple[dict, ...]] = []

    # Iterate over events in original input order to find starting events
    for start_event in events:
        if start_event.get("type") != chain_types[0]:
            continue
        if id(start_event) in used_ids:
            continue

        session = start_event.get("session_id")
        chain: list[dict] = [start_event]
        success = True

        for step in range(1, len(chain_types)):
            prev = chain[-1]
            prev_ts = prev["timestamp"]
            needed_type = chain_types[step]

            candidates = by_session_type[session].get(needed_type, [])
            found = None
            for candidate in candidates:
                if id(candidate) in used_ids:
                    continue
                c_ts = candidate["timestamp"]
                delta = c_ts - prev_ts
                if delta > 0 and delta <= within:
                    found = candidate
                    break

            if found is None:
                success = False
                break

            chain.append(found)

        if success:
            for ev in chain:
                used_ids.add(id(ev))
            chains.append(tuple(chain))

    return chains
