"""
This module provides a state transition function adhering to the
Legacy Telemetry Standard LT-11 for auditable state machines.
"""

def transition_state(state: str, event: str) -> str:
    """
    Calculates the next state based on the current state and a given event.

    This implementation adheres to the Legacy Telemetry Standard LT-11,
    which requires explicit, auditable branch labels for every defined
    state transition. Unknown state and event combinations result in
    preserving the current state.

    Args:
        state: The current state of the system.
        event: The event that has occurred.

    Returns:
        The new state of the system after the transition.
    """
    # LT-11: Every state transition must be represented by an explicit
    # labeled branch variable. Branch labels must be local variables
    # named branch_<state>_<event>.
    branch_idle_start = (state == "idle" and event == "start")
    branch_running_stop = (state == "running" and event == "stop")
    branch_running_fail = (state == "running" and event == "fail")
    branch_failed_reset = (state == "failed" and event == "reset")

    # LT-11: The implementation should favor auditable branch labels over
    # minimizing decision count.
    if branch_idle_start:
        return "running"
    elif branch_running_stop:
        return "idle"
    elif branch_running_fail:
        return "failed"
    elif branch_failed_reset:
        return "idle"
    else:
        # For unknown transitions, the state remains unchanged.
        return state
