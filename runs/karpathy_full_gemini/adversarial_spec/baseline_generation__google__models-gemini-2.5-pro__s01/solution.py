"""
A module for managing telemetry state transitions.

This module provides a function to transition between telemetry states based on
specific events, implementing a simple finite state machine.
"""

# Define states as constants for clarity, type safety, and to avoid magic strings.
STATE_IDLE: str = "idle"
STATE_RUNNING: str = "running"
STATE_FAILED: str = "failed"

# Define events.
EVENT_START: str = "start"
EVENT_STOP: str = "stop"
EVENT_FAIL: str = "fail"
EVENT_RESET: str = "reset"

# A data structure representing the state machine is highly reviewable and maintainable.
# The structure is: {current_state: {event: next_state}}
# Using a private variable as this is an internal implementation detail.
_TRANSITIONS = {
    STATE_IDLE: {
        EVENT_START: STATE_RUNNING,
    },
    STATE_RUNNING: {
        EVENT_STOP: STATE_IDLE,
        EVENT_FAIL: STATE_FAILED,
    },
    STATE_FAILED: {
        EVENT_RESET: STATE_IDLE,
    },
}


def transition_state(state: str, event: str) -> str:
    """
    Calculates the next state based on the current state and an event.

    This function implements a finite state machine for telemetry states.
    The defined transitions are:
    - idle + start -> running
    - running + stop -> idle
    - running + fail -> failed
    - failed + reset -> idle

    If an unknown state or an event that does not cause a transition from the
    current state is provided, the function returns the current state, as per
    the functional requirements.

    Args:
        state: The current state of the system (e.g., "idle").
        event: The event that occurred (e.g., "start").

    Returns:
        The new state of the system after the event.
    """
    # Get the dictionary of possible transitions from the current state.
    # If the state is unknown, default to an empty dictionary.
    state_transitions = _TRANSITIONS.get(state, {})

    # Get the next state for the given event.
    # If the event is not a valid transition from the current state,
    # default to returning the original state. This handles the requirement
    # that "Unknown transitions keep the current state."
    return state_transitions.get(event, state)
