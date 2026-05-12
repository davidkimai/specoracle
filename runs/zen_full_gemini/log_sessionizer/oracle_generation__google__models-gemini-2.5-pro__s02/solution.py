"""
A module for sessionizing user events from logs.
"""

import typing

__all__ = ["build_sessions"]


def _is_valid_event(event: typing.Any) -> bool:
    """
    Checks if an event is well-formed for sessionization.

    A valid event is a dictionary with a string 'user_id' and an integer
    'timestamp'.
    """
    if not isinstance(event, dict):
        return False

    user_id = event.get("user_id")
    timestamp = event.get("timestamp")

    return isinstance(user_id, str) and isinstance(timestamp, int)


def _prepare_events(events: list[dict]) -> list[dict]:
    """
    Filters for valid events and sorts them by user_id and then timestamp.
    """
    valid_events = [e for e in events if _is_valid_event(e)]
    return sorted(valid_events, key=lambda e: (e["user_id"], e["timestamp"]))


def build_sessions(events: list[dict], gap_seconds: int) -> list[dict]:
    """
    Builds user sessions from a list of events based on an inactivity gap.

    Each valid event must have a 'user_id' (str) and a 'timestamp' (int).
    Malformed events are skipped.

    Events are grouped by user and sorted by time. A new session is started
    for a user if the time gap since their last event exceeds 'gap_seconds'.

    Args:
        events: A list of event dictionaries.
        gap_seconds: The maximum time in seconds between two consecutive events
                     for them to be considered part of the same session.

    Returns:
        A list of session dictionaries, sorted by user_id and then session
        start time. Each session dictionary contains 'user_id', 'start'
        timestamp, 'end' timestamp, and 'count' of events.

    Raises:
        TypeError: If 'events' is not a list.
        ValueError: If 'gap_seconds' is not a non-negative integer.
    """
    if not isinstance(events, list):
        raise TypeError("Input 'events' must be a list.")
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError("Input 'gap_seconds' must be a non-negative integer.")

    sorted_events = _prepare_events(events)

    if not sorted_events:
        return []

    sessions = []

    # Initialize with the first event to start the first session.
    first_event = sorted_events[0]
    current_session = {
        "user_id": first_event["user_id"],
        "start": first_event["timestamp"],
        "end": first_event["timestamp"],
        "count": 1,
    }

    # Process remaining events.
    for event in sorted_events[1:]:
        is_different_user = event["user_id"] != current_session["user_id"]
        time_gap_exceeded = (event["timestamp"] - current_session["end"]) > gap_seconds

        if is_different_user or time_gap_exceeded:
            # The previous session has ended. Store it.
            sessions.append(current_session)

            # Start a new session with the current event.
            current_session = {
                "user_id": event["user_id"],
                "start": event["timestamp"],
                "end": event["timestamp"],
                "count": 1,
            }
        else:
            # The event belongs to the current session. Extend it.
            current_session["end"] = event["timestamp"]
            current_session["count"] += 1

    # Append the last processed session.
    sessions.append(current_session)

    return sessions
