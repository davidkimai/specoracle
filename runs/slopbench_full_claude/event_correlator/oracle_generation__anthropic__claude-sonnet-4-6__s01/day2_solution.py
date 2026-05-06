"""
event_correlator.py

Pairs each type-'A' event with the first later type-'B' event in the same
session that occurs within `within` seconds.

Day 2: Extended with chain_types parameter for arbitrary ordered-type chains.
"""

from collections import defaultdict


def correlate_events(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str] | None = None,
) -> list[tuple[dict, ...]]:
    """
    Pair each 'A' event with the first later 'B' event in the same session_id
    whose timestamp is within `within` seconds of the 'A' event.

    When `chain_types` is provided, instead return chains of events matching
    the ordered types within the same session, with each adjacent step within
    `within` seconds.

    Parameters
    ----------
    events : list[dict]
        Each dict must contain at least:
            - 'type'       : str
            - 'session_id' : hashable
            - 'timestamp'  : numeric (seconds)
    within : int
        Maximum allowed time delta (inclusive) in seconds between adjacent
        events in a pair or chain.
    chain_types : list[str] | None
        When provided, specifies the ordered sequence of event types to chain.
        Must contain at least two types.  Overrides the default A->B pairing.

    Returns
    -------
    list[tuple[dict, ...]]
        Ordered list of event tuples.  In the default (chain_types=None) mode
        each tuple is a 2-tuple (A_event, B_event).  In chain mode each tuple
        has len(chain_types) elements.

        Each event at position 0 in a chain appears at most once; later
        positions may be reused if multiple chains qualify (consistent with the
        original "first later B" semantics).
    """
    if within < 0:
        raise ValueError(f"'within' must be non-negative, got {within!r}")

    _validate_events(events)

    if chain_types is not None:
        if len(chain_types) < 2:
            raise ValueError(
                f"'chain_types' must contain at least two types, got {chain_types!r}"
            )
        return _build_chains(events, within=within, chain_types=chain_types)

    # ------------------------------------------------------------------
    # Original A -> B pairing behaviour
    # ------------------------------------------------------------------
    sorted_events = sorted(events, key=lambda e: e["timestamp"])

    b_by_session: dict = defaultdict(list)
    for event in sorted_events:
        if event["type"] == "B":
            b_by_session[event["session_id"]].append(event)

    pairs: list[tuple[dict, ...]] = []

    for a_event in sorted_events:
        if a_event["type"] != "A":
            continue
        partner = _first_matching_b(a_event, b_by_session, within)
        if partner is not None:
            pairs.append((a_event, partner))

    return pairs


# ---------------------------------------------------------------------------
# Chain builder (Day 2)
# ---------------------------------------------------------------------------

def _build_chains(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str],
) -> list[tuple[dict, ...]]:
    """
    Build all chains of events whose types match *chain_types* in order,
    within the same session, with each adjacent step within *within* seconds.

    The anchor (chain_types[0]) is consumed at most once per chain (greedy,
    first match at each subsequent step).
    """
    sorted_events = sorted(events, key=lambda e: e["timestamp"])

    # Group events by (session_id, type) for quick forward lookup.
    by_session_type: dict = defaultdict(list)
    for event in sorted_events:
        by_session_type[(event["session_id"], event["type"])].append(event)

    chains: list[tuple[dict, ...]] = []

    anchor_type = chain_types[0]
    for anchor_event in sorted_events:
        if anchor_event["type"] != anchor_type:
            continue

        chain: list[dict] = [anchor_event]
        current = anchor_event
        broken = False

        for next_type in chain_types[1:]:
            nxt = _first_event_after(
                current,
                by_session_type[(current["session_id"], next_type)],
                within,
            )
            if nxt is None:
                broken = True
                break
            chain.append(nxt)
            current = nxt

        if not broken:
            chains.append(tuple(chain))

    return chains


def _first_event_after(
    prev: dict,
    candidates: list[dict],
    within: int,
) -> dict | None:
    """Return the first event in *candidates* (sorted by timestamp) that is
    strictly later than *prev* and within *within* seconds."""
    prev_time = prev["timestamp"]
    for event in candidates:
        t = event["timestamp"]
        if t > prev_time and (t - prev_time) <= within:
            return event
        if t > prev_time + within:
            break
    return None


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
        if b_time > a_time + within:
            break

    return None
