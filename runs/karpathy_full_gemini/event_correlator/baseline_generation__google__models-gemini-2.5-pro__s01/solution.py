"""
A module for correlating events based on type, session, and time proximity.
"""

import collections
from typing import Any, Dict, List, Tuple, Union

# A type hint for event timestamps, which can be integers or floats.
Timestamp = Union[int, float]

def correlate_events(
    events: List[Dict[str, Any]],
    *,
    within: int
) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Correlates events of type 'A' with subsequent events of type 'B'.

    For each session, this function pairs an event of type 'A' with the first
    subsequent event of type 'B' that occurs within a specified time window.
    Each event can only be part of one pair.

    Args:
        events: A list of event dictionaries. Each dictionary must contain
                'session_id', a numeric 'timestamp', and 'event_type'.
        within: The maximum time delta in seconds between an 'A' event and a 'B'
                event for them to be considered a correlated pair.

    Returns:
        A list of tuples, where each tuple contains a pair of correlated
        event dictionaries (event_A, event_B).

    Raises:
        TypeError: If 'events' is not a list, an item in 'events' is not a
                   dictionary, or an event's timestamp is not numeric.
        ValueError: If 'within' is negative, or an event dictionary is missing
                    a required key ('session_id', 'timestamp', 'event_type').
    """
    if not isinstance(events, list):
        raise TypeError("Input 'events' must be a list.")
    if not isinstance(within, int) or within < 0:
        raise ValueError("'within' must be a non-negative integer.")

    # 1. Group events by session ID after initial validation.
    sessions: Dict[Any, List[Dict[str, Any]]] = collections.defaultdict(list)
    for i, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"Event at index {i} is not a dictionary.")

        try:
            session_id = event['session_id']
            timestamp = event['timestamp']
            # Access event_type to ensure it exists, though it is only used later.
            _ = event['event_type']
        except KeyError as e:
            raise ValueError(f"Event at index {i} is missing required key: {e}")

        if not isinstance(timestamp, (int, float)):
            raise TypeError(
                f"Event at index {i} has a non-numeric timestamp: {timestamp!r}"
            )

        sessions[session_id].append(event)

    correlated_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

    # 2. Process each session independently.
    for session_events in sessions.values():
        # Sort events chronologically to process them in order.
        session_events.sort(key=lambda e: e['timestamp'])

        # A queue to hold type 'A' events waiting for a 'B' to be paired with.
        unmatched_a_events: collections.deque[Dict[str, Any]] = collections.deque()

        for event in session_events:
            event_type = event.get('event_type')

            if event_type == 'A':
                unmatched_a_events.append(event)
            elif event_type == 'B':
                # This is event_B. Try to find a matching event_A from the queue.
                while unmatched_a_events:
                    # Peek at the oldest unmatched 'A' event.
                    event_a = unmatched_a_events[0]
                    time_delta = event['timestamp'] - event_a['timestamp']

                    if time_delta > within:
                        # This 'A' event is too old for this 'B' and any
                        # subsequent 'B's (since events are sorted). Discard it.
                        unmatched_a_events.popleft()
                        continue
                    else:
                        # As events are sorted, time_delta is non-negative.
                        # A valid pair is found: the oldest 'A' event within
                        # the time window is paired with this 'B' event.
                        correlated_pairs.append((event_a, event))
                        unmatched_a_events.popleft()  # 'A' is now matched.
                        break  # 'B' is now matched, so move to the next event.

    return correlated_pairs
