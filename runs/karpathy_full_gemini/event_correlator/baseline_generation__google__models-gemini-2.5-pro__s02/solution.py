# -*- coding: utf-8 -*-
"""
A module for correlating events based on type, session, and time proximity.
"""

import collections
from typing import Any

def correlate_events(
    events: list[dict[str, Any]], *, within: int
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """
    Pairs event type 'A' with the first later type 'B' in the same session.

    The correlation is valid only if the time difference between the 'A' event
    and the subsequent 'B' event is no more than the specified 'within'
    duration in seconds.

    Each 'A' event is paired with at most one 'B' event (the first one that
    meets the criteria). Events are processed chronologically within each session.

    Args:
        events: A list of event dictionaries. Each dictionary is expected to have
                'session_id', 'timestamp' (a numerical value, e.g., Unix time),
                and 'event_type' keys.
        within: The maximum allowed time delta in seconds for a valid correlation.
                Must be a non-negative integer.

    Returns:
        A list of tuples, where each tuple contains a pair of correlated
        (event_A, event_B) dictionaries.

    Raises:
        ValueError: If 'within' is negative.
        KeyError: If an event dictionary is missing a required key
                  ('session_id', 'timestamp', 'event_type').
    """
    if within < 0:
        raise ValueError("'within' must be a non-negative integer.")

    correlated_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []

    # 1. Group events by session_id for efficient processing.
    sessions: dict[Any, list[dict[str, Any]]] = collections.defaultdict(list)
    for event in events:
        sessions[event['session_id']].append(event)

    # 2. Process each session independently.
    for session_events in sessions.values():
        # Sort events by timestamp to ensure chronological order.
        # This is crucial for finding the "first later" event.
        # A KeyError will be raised here if 'timestamp' is missing in any event.
        session_events.sort(key=lambda e: e['timestamp'])

        num_events = len(session_events)
        for i in range(num_events):
            event_a = session_events[i]

            if event_a['event_type'] == 'A':
                # Search for the first subsequent 'B' event within the time window.
                for j in range(i + 1, num_events):
                    event_b = session_events[j]

                    # Calculate time delta.
                    time_delta = event_b['timestamp'] - event_a['timestamp']

                    # Optimization: Since events are sorted by time, if the current
                    # event is outside the window, all subsequent events will be too.
                    if time_delta > within:
                        break

                    if event_b['event_type'] == 'B':
                        # Found the first matching 'B' event for this 'A'.
                        correlated_pairs.append((event_a, event_b))
                        # Break the inner loop to ensure we only pair with the *first*
                        # suitable 'B' event.
                        break

    return correlated_pairs
