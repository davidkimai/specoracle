"""
A module for managing telemetry state transitions.

This module provides a function to transition between telemetry states based on
events, following a predefined state machine.
"""

from typing import Final, Dict, Mapping

# --- State Definitions ---
STATE_IDLE: Final[str] = "idle"
STATE_RUNNING: Final[str] = "running"
STATE_FAILED: Final[str] = "failed"

# --- Event Definitions ---
EVENT_START: Final[str] = "start"
EVENT_STOP: Final[str] = "stop"
EVENT_FAIL: Final[str] = "fail"
EVENT_RESET: Final[str] = "reset"

# --- State Machine Transition Table ---
# This table defines the valid transitions for the state machine.
# The structure is a mapping from the current state to a mapping of
# events to the next state.
# Format: {current_state: {event: next_state}}
_TRANSITIONS: Final[Mapping[str, Dict[str, str]]] = {
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
    Calculates the next state based on the current state and a given event.

    The state machine follows these rules:
    - idle + start -> running
    - running + stop -> idle
    - running + fail -> failed
    - failed + reset -> idle

    If the combination of the current state and event does not match any
    of the defined transitions, the function returns the current state.

    Args:
        state: The current state of the system (e.g., "idle", "running").
        event: The event that has occurred (e.g., "start", "stop").

    Returns:
        The new state of the system. If the transition is not defined,
        the current state is returned unchanged.
    """
    # Get the dictionary of possible transitions for the current state.
    # If the current state is not in the transition table, this returns an
    # empty dictionary, which correctly handles unknown states.
    events_for_state = _TRANSITIONS.get(state, {})

    # Get the next state for the given event.
    # If the event is not a valid transition for the current state,
    # the original `state` is returned as the default value.
    return events_for_state.get(event, state)
