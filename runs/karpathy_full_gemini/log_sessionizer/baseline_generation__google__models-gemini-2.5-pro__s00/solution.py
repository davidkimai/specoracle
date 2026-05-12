"""
This module provides functionality to build user sessions from event data.

The main function, build_sessions, processes a list of events to group them
into sessions based on user activity and a specified time gap.
"""

import collections.abc
from typing import Any, Dict, List


def build_sessions(
    events: List[Dict[str, Any]], gap_seconds: int
) -> List[Dict[str, Any]]:
    """
    Builds user sessions from a list of events based on a time gap.

    A session is a sequence of events from a single user where the time
    difference between consecutive events is no greater than `gap_seconds`.

    Args:
        events: A list of event dictionaries. Each valid event must have
                a 'user_id' (str) and a 'timestamp' (int). Malformed events
                are skipped.
        gap_seconds: The maximum time in seconds between events to be
                     considered part of the same session. Must be a
                     non-negative integer.

    Returns:
        A list of session dictionaries, sorted by user_id and then session
        start time. Each session dictionary has the following keys:
        - 'user_id' (str): The ID of the user.
        - 'start' (int): The timestamp of the first event in the session.
        - 'end' (int): The timestamp of the last event in the session.
        - 'count' (int): The number of events in the session.

    Raises:
        TypeError: If `events` is not a sequence.
        ValueError: If `gap_seconds` is not a non-negative integer.
    """
    if not isinstance(events, collections.abc.Sequence):
        raise TypeError("events must be a sequence.")
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError("gap_seconds must be a non-negative integer.")

    # Step 1: Filter out malformed events. A valid event is a dict with a
    # string 'user_id' and an integer 'timestamp'.
    valid_events = []
    for event in events:
        if (
            isinstance(event, dict)
            and "user_id" in event
            and isinstance(event.get("user_id"), str)
            and "timestamp" in event
            and isinstance(event.get("timestamp"), int)
        ):
            valid_events.append(event)

    if not valid_events:
        return []

    # Step 2: Sort events primarily by user_id and secondarily by timestamp.
    # This groups all events for a user together and in chronological order.
    valid_events.sort(key=lambda e: (e["user_id"], e["timestamp"]))

    # Step 3: Iterate through sorted events to build sessions.
    sessions = []
    # Initialize the first session with the first event.
    first_event = valid_events[0]
    current_session = {
        "user_id": first_event["user_id"],
        "start": first_event["timestamp"],
        "end": first_event["timestamp"],
        "count": 1,
    }

    # Iterate from the second event onwards.
    for event in valid_events[1:]:
        user_id = event["user_id"]
        timestamp = event["timestamp"]

        # Check if the event extends the current session.
        # This requires the same user and a time gap within the limit.
        is_same_user = user_id == current_session["user_id"]
        is_within_gap = timestamp - current_session["end"] <= gap_seconds

        if is_same_user and is_within_gap:
            # Extend the current session.
            current_session["end"] = timestamp
            current_session["count"] += 1
        else:
            # The current session has ended. Add it to the list.
            sessions.append(current_session)
            # Start a new session with the current event.
            current_session = {
                "user_id": user_id,
                "start": timestamp,
                "end": timestamp,
                "count": 1,
            }

    # Step 4: Append the very last session after the loop finishes.
    sessions.append(current_session)

    # The resulting sessions list is already sorted by user_id and then start
    # time because of the initial sort of events.
    return sessions
