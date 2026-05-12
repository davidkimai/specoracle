import operator
from typing import Any, Dict, List

Event = Dict[str, Any]
Session = Dict[str, Any]


def _validate_event(event: Event) -> bool:
    """
    Checks if an event dictionary is well-formed.

    A valid event is a dictionary containing a string 'user_id' and an
    integer 'timestamp'.
    """
    if not isinstance(event, dict):
        return False

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    if not isinstance(user_id, str) or not isinstance(timestamp, int):
        return False

    return True


def _filter_and_sort_events(events: List[Event]) -> List[Event]:
    """
    Filters for valid events and sorts them by user_id then timestamp.
    """
    valid_events = [e for e in events if _validate_event(e)]
    valid_events.sort(key=operator.itemgetter("user_id", "timestamp"))
    return valid_events


def _create_new_session(event: Event) -> Session:
    """
    Creates a new session dictionary from a single event.
    """
    return {
        "user_id": event["user_id"],
        "start": event["timestamp"],
        "end": event["timestamp"],
        "count": 1,
    }


def build_sessions(events: List[Event], gap_seconds: int) -> List[Session]:
    """
    Builds user sessions from a list of events based on an inactivity gap.

    Each valid event must be a dictionary with a 'user_id' (str) and
    a 'timestamp' (int). Malformed events are skipped.

    Events are grouped by user and sorted by time. A new session is started
    for a user if the time elapsed since their last event exceeds gap_seconds.

    Args:
        events: A list of event dictionaries.
        gap_seconds: The maximum time in seconds between consecutive events
                     in the same session.

    Returns:
        A list of session dictionaries, sorted by user_id and session
        start time. Each session includes 'user_id', 'start', 'end',
        and 'count'.

    Raises:
        ValueError: If gap_seconds is not a non-negative integer.
    """
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError("gap_seconds must be a non-negative integer.")

    sorted_events = _filter_and_sort_events(events)

    if not sorted_events:
        return []

    sessions: List[Session] = []
    current_session = _create_new_session(sorted_events[0])

    for i in range(1, len(sorted_events)):
        prev_event = sorted_events[i - 1]
        curr_event = sorted_events[i]

        is_new_user = curr_event["user_id"] != prev_event["user_id"]
        time_gap_exceeded = (
            curr_event["timestamp"] - prev_event["timestamp"] > gap_seconds
        )

        if is_new_user or time_gap_exceeded:
            sessions.append(current_session)
            current_session = _create_new_session(curr_event)
        else:
            current_session["end"] = curr_event["timestamp"]
            current_session["count"] += 1

    sessions.append(current_session)

    return sessions
