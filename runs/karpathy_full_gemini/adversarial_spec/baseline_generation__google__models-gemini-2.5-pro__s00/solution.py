"""
A module for managing telemetry state transitions.

This module provides a function to transition between telemetry states based on
events, implementing a simple finite state machine.
"""

import typing

# The state transition table defines the finite state machine.
# A nested dictionary where the outer key is the current state,
# and the inner dictionary maps an event to the next state.
# This structure makes the state machine's logic explicit and easy to review.
_TRANSITIONS: typing.Final[typing.Dict[str, typing.Dict[str, str]]] = {
    'idle': {
        'start': 'running',
    },
    'running': {
        'stop': 'idle',
        'fail': 'failed',
    },
    'failed': {
        'reset': 'idle',
    },
}


def transition_state(state: str, event: str) -> str:
    """
    Calculates the next state in a telemetry state machine.

    The state machine has the following transitions:
    - idle + start -> running
    - running + stop -> idle
    - running + fail -> failed
    - failed + reset -> idle

    If an unknown state or an event that does not cause a transition
    is provided, the current state is returned. This ensures the function
    is robust against unexpected inputs.

    Args:
        state: The current state of the machine (e.g., 'idle', 'running').
        event: The event that occurred (e.g., 'start', 'stop').

    Returns:
        The new state of the machine.
    """
    # Using .get() with a default value provides a safe way to handle
    # undefined states and events without raising a KeyError.
    #
    # 1. _TRANSITIONS.get(state, {}):
    #    - If `state` is a valid key in the transition table (e.g., 'idle'),
    #      it returns the corresponding dictionary of event transitions.
    #    - If `state` is not a key (an unknown state), it returns an empty
    #      dictionary, `{}`, as a default.
    #
    # 2. .get(event, state):
    #    - This is called on the result of the first get().
    #    - If an event transition is defined (e.g., event 'start' for state
    #      'idle'), it returns the new state (e.g., 'running').
    #    - If the event is not defined for the current state, or if the state
    #      itself was unknown (operating on `{}`), it returns the original
    #      `state` as the default value.
    return _TRANSITIONS.get(state, {}).get(event, state)
