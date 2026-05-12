import collections
from typing import Any, Dict, List, Tuple


def correlate_events(
    events: List[Dict[str, Any]], *, within: int
) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """Pairs event type 'A' with the first later type 'B' in the same session.

    The time delta between the 'A' and 'B' event must be no more than
    the value of `within` in seconds. An event can only be part of one pair.
    For each 'A' event, this function finds the first subsequent 'B' event
    in the same session that meets the time criteria. Once a 'B' event is
    paired, it cannot be paired with another 'A' event.

    Args:
        events: A list of event dictionaries. Each dictionary is expected to
                have 'session_id', 'timestamp', and 'event_type' keys.
        within: The maximum time in seconds between an 'A' event and a
                subsequent 'B' event for them to be correlated.

    Returns:
        A list of tuples, where each tuple contains the paired 'A' and 'B'
        event dictionaries: [(event_a, event_b), ...].
    """
    sessions: Dict[Any, List[Dict[str, Any]]] = collections.defaultdict(list)
    for event in events:
        if "session_id" in event:
            sessions[event["session_id"]].append(event)

    all_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

    for session_events in sessions.values():
        # Sort events chronologically. This is crucial for finding the "first
        # later" event efficiently and correctly. A missing 'timestamp' key
        # will raise a KeyError.
        session_events.sort(key=lambda e: e["timestamp"])

        used_b_indices = set()
        num_events = len(session_events)

        for i in range(num_events):
            event_a = session_events[i]
            if event_a.get("event_type") != "A":
                continue

            # For each 'A' event, find the first subsequent, unused 'B' event
            # that is within the specified time window.
            for j in range(i + 1, num_events):
                if j in used_b_indices:
                    continue

                event_b = session_events[j]
                if event_b.get("event_type") == "B":
                    time_delta = event_b["timestamp"] - event_a["timestamp"]

                    if 0 <= time_delta <= within:
                        # A valid pair is found.
                        all_pairs.append((event_a, event_b))
                        used_b_indices.add(j)
                        # An 'A' event pairs with only the *first* valid 'B',
                        # so we break the inner loop after finding one.
                        break

    return all_pairs
