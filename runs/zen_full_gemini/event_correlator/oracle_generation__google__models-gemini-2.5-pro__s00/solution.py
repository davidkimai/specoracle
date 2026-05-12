import collections
from typing import Any, Dict, List, Tuple

# A type alias for an event dictionary to improve readability within the module.
Event = Dict[str, Any]


def _validate_event(event: Event) -> None:
    """
    Checks if an event dictionary has the required structure and types.

    Raises:
        TypeError: If `event` is not a dictionary or if key values have
                   incorrect types.
        ValueError: If `event` is missing required keys.
    """
    if not isinstance(event, dict):
        raise TypeError(f"Event must be a dictionary, but got {type(event).__name__}.")

    required_keys = {"session_id", "timestamp", "event_type"}
    missing_keys = required_keys - set(event.keys())
    if missing_keys:
        raise ValueError(
            f"Event is missing required keys: {', '.join(sorted(missing_keys))}."
        )

    if not isinstance(event["timestamp"], (int, float)):
        raise TypeError(
            "Event 'timestamp' must be a number (int or float), "
            f"but got {type(event['timestamp']).__name__}."
        )

    if not isinstance(event["event_type"], str):
        raise TypeError(
            "Event 'event_type' must be a string, "
            f"but got {type(event['event_type']).__name__}."
        )


def _group_and_sort_events(events: List[Event]) -> Dict[Any, List[Event]]:
    """
    Groups events by session_id and sorts each group by timestamp.

    Args:
        events: A list of event dictionaries to process.

    Returns:
        A dictionary where keys are session IDs and values are lists of
        events for that session, sorted chronologically.
    """
    sessions = collections.defaultdict(list)
    for event in events:
        _validate_event(event)
        sessions[event["session_id"]].append(event)

    for session_id in sessions:
        # Sort events within each session by their timestamp.
        sessions[session_id].sort(key=lambda e: e["timestamp"])

    return sessions


def _find_pairs_in_session(
    session_events: List[Event], within: int
) -> List[Tuple[Event, Event]]:
    """
    Finds all ('A', 'B') event pairs in a single, sorted list of events.

    For each 'A' event, it finds the first subsequent 'B' event that occurs
    within the specified time window.

    Args:
        session_events: A list of events for a single session, sorted by
                        timestamp.
        within: The maximum time delta for a valid correlation.

    Returns:
        A list of correlated (A, B) event pairs.
    """
    pairs = []
    num_events = len(session_events)

    for i in range(num_events):
        event_a = session_events[i]
        if event_a["event_type"] != "A":
            continue

        # Search for the first matching 'B' event for the current 'A' event.
        for j in range(i + 1, num_events):
            event_b = session_events[j]

            time_delta = event_b["timestamp"] - event_a["timestamp"]
            if time_delta > within:
                # Since events are sorted by time, no subsequent event in this
                # session can be a match for the current event_a.
                break

            if event_b["event_type"] == "B":
                # Found the first 'B' event within the time window.
                pairs.append((event_a, event_b))
                # Stop searching for this event_a and move to the next.
                break

    return pairs


def correlate_events(
    events: List[Dict], *, within: int
) -> List[Tuple[Dict, Dict]]:
    """
    Pairs event type 'A' with the first later type 'B' in the same session.

    The time delta between the 'A' and 'B' events must be no more than
    the `within` parameter in seconds. Each 'A' event is paired at most once.

    Args:
        events: A list of event dictionaries. Each dictionary must contain
                'session_id', 'timestamp' (a number), and 'event_type' (a string).
        within: The maximum time delta in seconds for a valid pair. Must be
                a non-negative integer.

    Returns:
        A list of tuples, where each tuple contains the paired (A, B) events.
        The list is ordered by session ID, then by the timestamp of the 'A' event.

    Raises:
        TypeError: If `events` is not a list, an element is not a dict,
                   or `within` is not an integer.
        ValueError: If an event dictionary is missing required keys, or if
                    `within` is negative.
    """
    if not isinstance(events, list):
        raise TypeError(f"Expected a list of events, but got {type(events).__name__}.")
    if not isinstance(within, int):
        raise TypeError(
            f"Parameter 'within' must be an integer, but got {type(within).__name__}."
        )
    if within < 0:
        raise ValueError("Parameter 'within' cannot be negative.")

    grouped_sessions = _group_and_sort_events(events)

    all_correlated_pairs = []
    # Sort session keys to ensure deterministic output order.
    # This assumes session IDs are comparable.
    sorted_session_ids = sorted(grouped_sessions.keys())

    for session_id in sorted_session_ids:
        session_events = grouped_sessions[session_id]
        session_pairs = _find_pairs_in_session(session_events, within)
        all_correlated_pairs.extend(session_pairs)

    return all_correlated_pairs
