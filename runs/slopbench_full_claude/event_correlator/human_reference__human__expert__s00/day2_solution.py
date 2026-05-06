from __future__ import annotations


def correlate_events(
    events: list[dict],
    *,
    within: int,
    chain_types: list[str] | None = None,
) -> list[tuple[dict, ...]]:
    ordered = sorted(events, key=lambda row: row.get('ts', 0))

    if chain_types is not None:
        if len(chain_types) < 2:
            raise ValueError("chain_types must contain at least two type labels")
        return _chain(ordered, chain_types=chain_types, within=within)

    # Original behaviour: pair A with first later B in same session within window
    pairs: list[tuple[dict, ...]] = []
    for left in ordered:
        if left.get('type') != 'A':
            continue
        for right in ordered:
            if right.get('session_id') != left.get('session_id') or right.get('type') != 'B':
                continue
            if 0 < right.get('ts', 0) - left.get('ts', 0) <= within:
                pairs.append((left, right))
                break
    return pairs


def _chain(
    ordered: list[dict],
    *,
    chain_types: list[str],
    within: int,
) -> list[tuple[dict, ...]]:
    """Return all chains of events matching chain_types in order within the same
    session, with each adjacent pair within *within* seconds."""

    # Group events by session_id, preserving sort order
    from collections import defaultdict
    by_session: dict = defaultdict(list)
    for event in ordered:
        by_session[event.get('session_id')].append(event)

    results: list[tuple[dict, ...]] = []

    for session_events in by_session.values():
        # Build chains incrementally.
        # partial_chains[i] holds all partial chains whose last element matched
        # chain_types[i].
        partial_chains: list[list[list[dict]]] = [[] for _ in chain_types]

        for event in session_events:
            etype = event.get('type')
            ts = event.get('ts', 0)

            # Walk chain_types in reverse so we don't extend a chain in the
            # same pass that we started it.
            for i in range(len(chain_types) - 1, -1, -1):
                if etype != chain_types[i]:
                    continue

                if i == 0:
                    # Start a new chain
                    partial_chains[0].append([event])
                else:
                    # Extend chains from the previous step
                    new_chains = []
                    for chain in partial_chains[i - 1]:
                        prev_ts = chain[-1].get('ts', 0)
                        delta = ts - prev_ts
                        if 0 < delta <= within:
                            new_chains.append(chain + [event])
                    if i == len(chain_types) - 1:
                        # Completed chains
                        for chain in new_chains:
                            results.append(tuple(chain))
                    else:
                        partial_chains[i].extend(new_chains)

    return results
