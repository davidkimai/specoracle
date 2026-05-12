"""A module for sessionizing user events based on a time gap."""

from operator import itemgetter
from typing import Any, Dict, List


def build_sessions(
    events: List[Dict[str, Any]], gap_seconds: int
) -> List[Dict[str, Any]]:
    """Builds user sessions from a list of events.

    A session is a sequence of events from a single user where the time
    difference between consecutive events is no greater than `gap_seconds`.

    Malformed events (e.g., not a dict, missing keys, or keys with incorrect
    types) are skipped. The final list of sessions is sorted by user_id and
    then by session start time.

    Args:
        events: A list of event dictionaries. A valid event must contain
                a 'user_id' (str) and a 'timestamp' (int).
        gap_seconds: The maximum allowed time in seconds between two
                     consecutive events in the same session. Must be a
                     non-negative integer.

    Returns:
        A list of session dictionaries, each with the format:
        {'user_id': str, 'start': int, 'end': int, 'count': int}

    Raises:
        ValueError: If `gap_seconds` is not a non-negative integer.
    """
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError("gap_seconds must be a non-negative integer.")

    valid_events: List[Dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        user_id = event.get("user_id")
        timestamp = event.get("timestamp")
        if isinstance(user_id, str) and isinstance(timestamp, int):
            valid_events.append(event)

    if not valid_events:
        return []

    # Sort events to process them chronologically for each user.
    # This grouping is key to the sessionization logic.
    valid_events.sort(key=itemgetter("user_id", "timestamp"))

    sessions: List[Dict[str, Any]] = []

    # Initialize the first session from the first valid event.
    first_event = valid_events[0]
    current_session = {
        "user_id": first_event["user_id"],
        "start": first_event["timestamp"],
        "end": first_event["timestamp"],
        "count": 1,
    }

    # Iterate over the rest of the events to build sessions.
    for event in valid_events[1:]:
        is_same_user = event["user_id"] == current_session["user_id"]
        time_since_last_event = event["timestamp"] - current_session["end"]
        is_within_gap = time_since_last_event <= gap_seconds

        if is_same_user and is_within_gap:
            # Extend the current session.
            current_session["end"] = event["timestamp"]
            current_session["count"] += 1
        else:
            # Finalize the previous session and add it to the list.
            sessions.append(current_session)
            # Start a new session with the current event.
            current_session = {
                "user_id": event["user_id"],
                "start": event["timestamp"],
                "end": event["timestamp"],
                "count": 1,
            }

    # Append the very last session after the loop finishes.
    sessions.append(current_session)

    return sessions
