import operator
from typing import Any, Dict, List

def build_sessions(events: List[Dict[str, Any]], gap_seconds: int) -> List[Dict[str, Any]]:
    """
    Analyzes a list of user events to build user sessions.

    A session is a sequence of events from a single user where the time gap
    between consecutive events is no greater than `gap_seconds`.

    Args:
        events: A list of event dictionaries. Each valid event must contain
                'user_id' (str) and 'timestamp' (int). Malformed events
                (e.g., missing keys, wrong types) are ignored.
        gap_seconds: The maximum allowed time in seconds between two
                     consecutive events in the same session.

    Returns:
        A list of session dictionaries, sorted by user_id and then by session
        start time. Each session dictionary contains:
        - 'user_id': The ID of the user.
        - 'start': The timestamp of the first event in the session.
        - 'end': The timestamp of the last event in the session.
        - 'count': The number of events in the session.
    """
    valid_events = []
    for event in events:
        if not isinstance(event, dict):
            continue
            
        user_id = event.get('user_id')
        timestamp = event.get('timestamp')

        if user_id is None or not isinstance(timestamp, int):
            continue
            
        valid_events.append(event)

    if not valid_events:
        return []

    # Sort events primarily by user_id, secondarily by timestamp.
    # This groups all events for a user together and in chronological order.
    valid_events.sort(key=operator.itemgetter('user_id', 'timestamp'))

    sessions = []
    
    # Initialize the first session from the first valid, sorted event.
    first_event = valid_events[0]
    current_session = {
        'user_id': first_event['user_id'],
        'start': first_event['timestamp'],
        'end': first_event['timestamp'],
        'count': 1,
    }

    # Iterate through the rest of the events to build sessions.
    for i in range(1, len(valid_events)):
        event = valid_events[i]
        
        is_same_user = event['user_id'] == current_session['user_id']
        time_since_last_event = event['timestamp'] - current_session['end']
        is_within_gap = time_since_last_event <= gap_seconds

        if is_same_user and is_within_gap:
            # This event belongs to the current session. Extend the session.
            current_session['end'] = event['timestamp']
            current_session['count'] += 1
        else:
            # This event starts a new session. Finalize the old one.
            sessions.append(current_session)
            # Start a new session with the current event.
            current_session = {
                'user_id': event['user_id'],
                'start': event['timestamp'],
                'end': event['timestamp'],
                'count': 1,
            }

    # Append the last session after the loop finishes.
    sessions.append(current_session)

    return sessions
