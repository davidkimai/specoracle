"""
This module provides functionality to group user events into sessions based on inactivity gaps.
"""

from typing import Any, Dict, List

# A type alias for clarity, representing an event dictionary.
Event = Dict[str, Any]

# A type alias for clarity, representing a session dictionary.
Session = Dict[str, Any]


def _is_valid_event(event: Any) -> bool:
    """
    Checks if an event is well-formed.

    A valid event is a dictionary containing a string 'user_id' and an
    integer 'timestamp'.

    Args:
        event: The event object to validate.

    Returns:
        True if the event is valid, False otherwise.
    """
    if not isinstance(event, dict):
        return False

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    if not isinstance(user_id, str) or not isinstance(timestamp, int):
        return False

    return True


def _create_session_from_event(event: Event) -> Session:
    """
    Creates a new session from a single event.

    Args:
        event: The event that starts the session.

    Returns:
        A new session dictionary.
    """
    return {
        "user_id": event["user_id"],
        "start": event["timestamp"],
        "end": event["timestamp"],
        "count": 1,
    }


def _extend_session(session: Session, event: Event) -> None:
    """
    Extends an existing session with a subsequent event.

    This function mutates the session dictionary by updating its 'end'
    timestamp and incrementing its 'count'.

    Args:
        session: The session to extend.
        event: The event to add to the session.
    """
    session["end"] = event["timestamp"]
    session["count"] += 1


def build_sessions(events: List[Event], gap_seconds: int) -> List[Session]:
    """
    Groups a list of user events into sessions based on an inactivity gap.

    Events are first filtered for validity and then sorted by user and time.
    A new session is started for a user if the time since their last event
    exceeds `gap_seconds`.

    Args:
        events: A list of event dictionaries. Each valid event must contain a
                'user_id' (str) and a 'timestamp' (int). Malformed events
                are ignored.
        gap_seconds: The maximum time in seconds between consecutive events
                     in the same session.

    Returns:
        A list of session dictionaries, sorted by 'user_id' and then by
        session 'start' time. Each session includes 'user_id', 'start'
        and 'end' timestamps, and the 'count' of events.

    Raises:
        ValueError: If `gap_seconds` is not a non-negative integer.
    """
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError("gap_seconds must be a non-negative integer.")

    valid_events = [e for e in events if _is_valid_event(e)]

    if not valid_events:
        return []

    valid_events.sort(key=lambda e: (e["user_id"], e["timestamp"]))

    sessions: List[Session] = []
    current_session = _create_session_from_event(valid_events[0])

    for event in valid_events[1:]:
        is_different_user = event["user_id"] != current_session["user_id"]
        time_gap_exceeded = (
            event["timestamp"] - current_session["end"] > gap_seconds
        )

        if is_different_user or time_gap_exceeded:
            sessions.append(current_session)
            current_session = _create_session_from_event(event)
        else:
            _extend_session(current_session, event)

    sessions.append(current_session)

    return sessions
