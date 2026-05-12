"""A module for correlating events based on type, session, and time window."""

import collections
from typing import Any, Dict, List, Tuple

# A type alias for an event dictionary for improved readability.
Event = Dict[str, Any]


def correlate_events(
    events: List[Event], *, within: int
) -> List[Tuple[Event, Event]]:
    """Pairs event type 'A' with the first later type 'B' in the same session.

    The correlation is valid only if the time delta between the 'A' and 'B'
    events is no more than the specified 'within' seconds. For a given
    event 'A', it will be paired with the earliest possible event 'B' that
    satisfies the conditions.

    Args:
        events: A list of event dictionaries. Each dictionary must contain
                'timestamp' (a sortable numeric value), 'session_id' (a
                hashable identifier), and 'event_type' (a string).
        within: The maximum time delta in seconds for a valid correlation.
                Must be a non-negative integer.

    Returns:
        A list of tuples, where each tuple contains a correlated
        (event_A, event_B) pair.

    Raises:
        ValueError: If 'within' is negative.
        KeyError: If an event is missing a required key ('session_id',
                  'timestamp', 'event_type').
        TypeError: If an event is not a dictionary or if timestamps from the
                   same session are not comparable.
    """
    if not isinstance(within, int) or within < 0:
        raise ValueError("'within' must be a non-negative integer.")

    # 1. Group events by session_id.
    sessions: Dict[Any, List[Event]] = collections.defaultdict(list)
    for event in events:
        try:
            session_id = event["session_id"]
            sessions[session_id].append(event)
        except TypeError:
            raise TypeError(f"Event must be a dictionary, but got: {type(event)}")
        except KeyError:
            raise KeyError(f"Event is missing required key 'session_id': {event}")

    correlated_pairs: List[Tuple[Event, Event]] = []

    for session_id, session_events in sessions.items():
        # 2. Sort events chronologically to enable efficient searching.
        try:
            session_events.sort(key=lambda e: e["timestamp"])
        except KeyError:
            # Find the problematic event for a better error message.
            for evt in session_events:
                if "timestamp" not in evt:
                    raise KeyError(
                        f"Event in session '{session_id}' is missing "
                        f"'timestamp' key: {evt}"
                    )
            # Fallback for other key-related errors during sorting.
            raise
        except TypeError:
            raise TypeError(
                f"Timestamps in session '{session_id}' must be comparable."
            )

        # 3. Find A-B pairs within the time window.
        num_events = len(session_events)
        for i in range(num_events):
            event_a = session_events[i]
            # Enforce that 'event_type' must exist.
            if event_a["event_type"] == "A":
                # Search for the *first* subsequent 'B' event.
                for j in range(i + 1, num_events):
                    event_b = session_events[j]

                    time_delta = event_b["timestamp"] - event_a["timestamp"]

                    # Optimization: If the delta exceeds 'within', no
                    # subsequent event in this sorted list can be a match.
                    if time_delta > within:
                        break

                    if event_b["event_type"] == "B":
                        # Found the first valid 'B' for this 'A'.
                        correlated_pairs.append((event_a, event_b))
                        # Stop searching for this 'A' and move to the next.
                        break

    return correlated_pairs
