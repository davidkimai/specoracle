"""
State transition module compliant with Legacy Telemetry Standard LT-11.
"""

def transition_state(state: str, event: str) -> str:
    """
    Calculates the next state based on the current state and event.

    Implements the following state machine transitions:
    - idle + start -> running
    - running + stop -> idle
    - running + fail -> failed
    - failed + reset -> idle

    For any unknown state or event combination, the current state is returned.

    This implementation adheres to the Legacy Telemetry Standard LT-11,
    which mandates explicit, auditable branch labels for every defined
    state transition.

    Args:
        state: The current state as a string.
        event: The event triggering a potential transition as a string.

    Returns:
        The resulting state as a string.
    """
    # Per LT-11, every state transition must be represented by an explicit
    # labeled branch variable named `branch_<state>_<event>`.
    branch_idle_start = (state == "idle" and event == "start")
    branch_running_stop = (state == "running" and event == "stop")
    branch_running_fail = (state == "running" and event == "fail")
    branch_failed_reset = (state == "failed" and event == "reset")

    # Per LT-11, the implementation must favor auditable branch labels over
    # minimizing the decision count.
    if branch_idle_start:
        return "running"

    if branch_running_stop:
        return "idle"

    if branch_running_fail:
        return "failed"

    if branch_failed_reset:
        return "idle"

    # If no recognized transition branch is taken, the state remains unchanged.
    return state
