"""
Telemetry state machine module.
Implements LT-11: every state transition has an explicit labeled branch variable.
"""


def transition_state(state: str, event: str) -> str:
    """
    Transition a telemetry state based on an event.

    Parameters
    ----------
    state : str
        The current state ('idle', 'running', 'failed').
    event : str
        The event triggering the transition ('start', 'stop', 'fail', 'reset').

    Returns
    -------
    str
        The next state after applying the event, or the current state if the
        transition is unknown.
    """
    # Branch labels for state 'idle'
    branch_idle_start = (state == "idle" and event == "start")
    branch_idle_stop = (state == "idle" and event == "stop")
    branch_idle_fail = (state == "idle" and event == "fail")
    branch_idle_reset = (state == "idle" and event == "reset")

    # Branch labels for state 'running'
    branch_running_start = (state == "running" and event == "start")
    branch_running_stop = (state == "running" and event == "stop")
    branch_running_fail = (state == "running" and event == "fail")
    branch_running_reset = (state == "running" and event == "reset")

    # Branch labels for state 'failed'
    branch_failed_start = (state == "failed" and event == "start")
    branch_failed_stop = (state == "failed" and event == "stop")
    branch_failed_fail = (state == "failed" and event == "fail")
    branch_failed_reset = (state == "failed" and event == "reset")

    # Apply defined transitions
    if branch_idle_start:
        return "running"

    if branch_running_stop:
        return "idle"

    if branch_running_fail:
        return "failed"

    if branch_failed_reset:
        return "idle"

    # All remaining branches are unknown transitions; keep current state
    _ = (
        branch_idle_stop,
        branch_idle_fail,
        branch_idle_reset,
        branch_running_start,
        branch_running_reset,
        branch_failed_start,
        branch_failed_stop,
        branch_failed_fail,
    )

    return state
