"""
This module provides functionality to sessionize user events based on time gaps.
"""

import typing


def build_sessions(
    events: typing.List[typing.Dict], gap_seconds: int
) -> typing.List[typing.Dict]:
    """
    Builds user sessions from a list of events.

    Each valid event must have a 'user_id' and an integer 'timestamp'. Events
    that are malformed (e.g., not a dict, missing required keys, or a
    non-integer timestamp) are skipped.

    Valid events are sorted by user_id and then by timestamp. For each user,
    a new session is started when the time gap from the user's previous
    event is greater than `gap_seconds`.

    Args:
        events: A list of event dictionaries.
        gap_seconds: The maximum allowed time in seconds between two
                     consecutive events in the same session. A gap
                     strictly greater than this value will start a new
                     session.

    Returns:
        A list of session dictionaries, sorted by user_id and then by the
        session's start time. Each session dictionary has the format:
        {
            "user_id": str,
            "start": int,
            "end": int,
            "count": int
        }
    """
    valid_events = []
    for event in events:
        if not isinstance(event, dict):
            continue

        user_id = event.get('user_id')
        timestamp = event.get('timestamp')

        if user_id is not None and isinstance(timestamp, int):
            valid_events.append(event)

    if not valid_events:
        return []

    # Sort events primarily by user_id, secondarily by timestamp.
    # This is crucial for processing events in the correct order for each user.
    valid_events.sort(key=lambda e: (e['user_id'], e['timestamp']))

    sessions = []
    current_session = None

    for event in valid_events:
        user_id = event['user_id']
        timestamp = event['timestamp']

        # A new session starts if:
        # 1. It's the first event being processed (current_session is None).
        # 2. The user_id for the event is different from the current session's user.
        # 3. The time gap since the last event for the current user is too large.
        if (current_session is None or
                user_id != current_session['user_id'] or
                (timestamp - current_session['end']) > gap_seconds):

            # If there was a previous session, finalize and add it to the list.
            if current_session is not None:
                sessions.append(current_session)

            # Start a new session with the current event.
            current_session = {
                "user_id": user_id,
                "start": timestamp,
                "end": timestamp,
                "count": 1
            }
        else:
            # Extend the current session: update the end time and event count.
            current_session['end'] = timestamp
            current_session['count'] += 1

    # After the loop, the last processed session needs to be appended.
    if current_session is not None:
        sessions.append(current_session)
