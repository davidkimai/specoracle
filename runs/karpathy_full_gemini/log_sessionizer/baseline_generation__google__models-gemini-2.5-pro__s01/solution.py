"""
A module for sessionizing user events based on a time gap.
"""

from typing import List, Dict, Any

def build_sessions(events: List[Dict[str, Any]], gap_seconds: int) -> List[Dict[str, Any]]:
    """
    Groups a list of user events into sessions.

    A session is a sequence of events from a single user where the time
    gap between consecutive events does not exceed a specified duration.

    Args:
        events: A list of event dictionaries. Each valid event must have a
                'user_id' and an integer 'timestamp'. Malformed events, such as
                those missing required keys or with non-integer timestamps, are
                skipped.
        gap_seconds: The maximum allowed time in seconds between two
                     consecutive events in the same session. Must be a
                     non-negative integer.

    Returns:
        A list of session dictionaries, sorted by user_id and then by
        session start time. Each session dictionary contains:
        - 'user_id': The ID of the user.
        - 'start': The timestamp of the first event in the session.
        - 'end': The timestamp of the last event in the session.
        - 'count': The number of events in the session.
    """
    if not isinstance(gap_seconds, int) or gap_seconds < 0:
        raise ValueError("gap_seconds must be a non-negative integer.")

    # Step 1: Filter and validate events.
    # An event is valid if it's a dict with 'user_id' and an integer 'timestamp'.
    valid_events = []
    for event in events:
        if (isinstance(event, dict) and
                'user_id' in event and
                isinstance(event.get('timestamp'), int)):
            valid_events.append(event)

    if not valid_events:
        return []

    # Step 2: Sort events first by user_id, then by timestamp.
    # This groups all events for a user together and orders them chronologically.
    valid_events.sort(key=lambda e: (e['user_id'], e['timestamp']))

    sessions = []
    # Initialize the first session with the first sorted event.
    current_session = {
        'user_id': valid_events[0]['user_id'],
        'start': valid_events[0]['timestamp'],
        'end': valid_events[0]['timestamp'],
        'count': 1,
    }

    # Step 3: Iterate through the rest of the events to build sessions.
    for i in range(1, len(valid_events)):
        event = valid_events[i]

        # Check if the event belongs to the current session.
        # It must be from the same user and within the allowed time gap.
        is_same_user = (event['user_id'] == current_session['user_id'])
        is_within_gap = (event['timestamp'] - current_session['end']) <= gap_seconds

        if is_same_user and is_within_gap:
            # Extend the current session.
            current_session['end'] = event['timestamp']
            current_session['count'] += 1
        else:
            # The current session has ended. Add it to our list.
            sessions.append(current_session)
            # Start a new session with the current event.
            current_session = {
                'user_id': event['user_id'],
                'start': event['timestamp'],
                'end': event['timestamp'],
                'count': 1,
            }

    # Step 4: Add the very last session to the list.
    sessions.append(current_session)

    # The sessions are naturally sorted by user_id and start time due to the
    # initial sort and processing order.
    return sessions
