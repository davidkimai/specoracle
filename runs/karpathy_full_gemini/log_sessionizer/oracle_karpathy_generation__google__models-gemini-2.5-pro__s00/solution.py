"""
A module for sessionizing user events from a list.
"""

from typing import Any, Dict, List


def build_sessions(
    events: List[Dict[str, Any]], gap_seconds: int
) -> List[Dict[str, Any]]:
    """
    Groups a list of user events into sessions based on inactivity.

    This function processes a list of event dictionaries, filters for valid
    events, sorts them by user and time, and then groups them into sessions.
    A new session is started for a user if the time elapsed since their last
    event exceeds `gap_seconds`.

    Args:
        events: A list of event dictionaries. A valid event is a dictionary
                containing at least a 'user_id' and an integer 'timestamp'.
                Events that do not meet this criteria are ignored.
        gap_seconds: An integer representing the maximum time in seconds
                     allowed between consecutive events within a single session.

    Returns:
        A list of session dictionaries, sorted by user_id and then by the
        session's start time. Each session
