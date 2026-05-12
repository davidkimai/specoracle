import collections
from typing import Any, Dict, List, Tuple

# A type alias for clarity in function signatures.
Event = Dict[str, Any]


def _validate_inputs(events: List[Event], within: int) -> None:
    """
    Performs top-level validation of the main function arguments.

    Raises:
        TypeError: If 'events' is not a list of dicts or 'within' is not an int.
        ValueError: If 'within' is a negative number.
    """
    if not isinstance(events, list):
        raise TypeError("'events' must be a list.")

    if not all(isinstance(e, dict) for e in events):
        raise TypeError("All items in 'events' must be dictionaries.")

    if not isinstance(within, int) or isinstance(within, bool):
        raise TypeError("'within' must be an integer.")

    if within < 0:
        raise ValueError("'within' must be a non-negative integer.")


def _group_and_sort_events(events: List[Event]) -> Dict[Any, List[Event]]:
    """
    Groups events by session_id and sorts the events within each session by timestamp.

    Also validates that each event has the required keys and that the timestamp
    is a numeric type.

    Returns:
        A dictionary mapping session_ids to a time-sorted list of events.

    Raises:
        ValueError: If an event is missing a required key.
        TypeError: If an event's timestamp is not a numeric type.
    """
    sessions = collections.defaultdict(list)
    for i, event in enumerate(events):
        try:
            session_id = event['session_id']
            timestamp = event['timestamp']
            # Ensure 'type' key exists, as it's crucial for correlation.
            _ = event['type']
        except KeyError as e:
            raise ValueError(f"Event at index {i} is missing required key: {e}")

        if not isinstance(timestamp, (int, float)):
            raise TypeError(
                f"Event at index {i} has a non-numeric timestamp: {timestamp!r}"
            )

        sessions[session_id].append(event)

    for session_events in sessions.values():
        session_events.sort(key=lambda e: e['timestamp'])

    return sessions


def _correlate_session_events(
    session_events: List[Event], within: int
) -> List[Tuple[Event, Event]]:
    """
    Finds correlated (A, B) event pairs within a single session's events.

    Assumes `session_events` is sorted by timestamp.

    Args:
        session_events: A time-sorted list of events for a single session.
        within: The maximum time delta for a correlation.

    Returns:
        A list of correlated (event_A, event_B) tuples.
    """
    pairs = []
    num_events = len(session_events)

    for i in range(num_events):
        event_a = session_events[i]
        if event_a.get('type') != 'A':
            continue

        # Search forward from the event after 'A' for the first 'B'.
        for j in range(i + 1, num_events):
            event_b = session_events[j]
            
            time_delta = event_b['timestamp'] - event_a['timestamp']

            if time_delta > within:
                # Since events are sorted by timestamp, no subsequent event
                # in this session can be a match for the current event_a.
                break

            if event_b.get('type') == 'B':
                # This is the first matching 'B' found for this 'A'
                # that is within the allowed time delta.
                pairs.append((event_a, event_b))
                
                # Stop searching for other 'B's for this specific 'A'.
                break
    return pairs


def correlate_events(
    events: List[Event], *, within: int
) -> List[Tuple[Event, Event]]:
    """
    Pairs event type 'A' with the first later type 'B' in the same session.

    The time delta between the 'A' and 'B' events must be no more than
    the value of `within` in seconds.

    Args:
        events: A list of event dictionaries. Each event must have 'session_id',
                'timestamp' (numeric), and 'type' keys.
        within: The maximum time delta in seconds for a valid correlation.

    Returns:
        A list of (event_A, event_B) tuples representing correlated pairs.

    Raises:
        TypeError: If inputs are of the wrong type.
        ValueError: If inputs have invalid values or an event has a bad structure.
    """
    _validate_inputs(events, within)
    if not events:
        return []

    sessions = _group_and_sort_events(events)

    all_correlated_pairs = []
    for session_events in sessions.values():
        correlated_pairs_in_session = _correlate_session_events(
            session_events, within
        )
        all_correlated_pairs.extend(correlated_pairs_in_session)

    return all_correlated_pairs
