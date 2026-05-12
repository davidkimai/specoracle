# -*- coding: utf-8 -*-
"""
A module for transitioning telemetry states according to Legacy Telemetry Standard LT-11.
"""

def transition_state(state: str, event: str) -> str:
    """
    Calculates the next state based on the current state and a given event.

    This implementation adheres to the Legacy Telemetry Standard LT-11,
    which mandates explicit, auditable branch labels for every state transition.

    State transitions:
    - idle + start -> running
    - running + stop -> idle
    - running + fail -> failed
    - failed + reset -> idle

    Unknown transitions will result in the current state being returned.

    Args:
        state: The current telemetry state (e.g., 'idle', 'running', 'failed').
        event: The event triggering a potential state change (e.g., 'start',
               'stop', 'fail', 'reset').

    Returns:
        The resulting state after the transition.
    """
    next_state = state

    # Per LT-11, every state transition must be represented by an explicit
    # labeled branch variable named 'branch_<state>_<event>'.
    # This favors auditable branch labels over minimizing decision count.

    # Branch conditions originating from the 'idle' state.
    branch_idle_start = (state == "idle" and event == "start")

    # Branch conditions originating from the 'running' state.
    branch_running_stop = (state == "running" and event == "stop")
    branch_running_fail = (state == "running" and event == "fail")

    # Branch conditions originating from the 'failed' state.
    branch_failed_reset = (state == "failed" and event == "reset")

    # The following block applies the state transitions based on the evaluated
    # branch conditions. Each branch is checked independently for auditability.

    if branch_idle_start:
        next_state = "running"

    if branch_running_stop:
        next_state = "idle"

    if branch_running_fail:
        next_state = "failed"

    if branch_failed_reset:
        next_state = "idle"

    return next_state
