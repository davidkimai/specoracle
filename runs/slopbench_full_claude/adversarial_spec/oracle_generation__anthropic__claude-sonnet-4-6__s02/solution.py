"""
Telemetry state machine module implementing LT-11 standard.
Every state transition is represented by an explicit labeled branch variable.
"""


def transition_state(state: str, event: str) -> str:
    """
    Compute the next telemetry state given the current state and an event.

    Parameters
    ----------
    state : str
        The current telemetry state.
    event : str
        The event triggering a potential state transition.

    Returns
    -------
    str
        The resulting state after applying the event.
    """
    # Branch: idle state transitions
    branch_idle_start = (state == "idle" and event == "start")
    branch_idle_other = (state == "idle" and not branch_idle_start)

    # Branch: running state transitions
    branch_running_stop = (state == "running" and event == "stop")
    branch_running_fail = (state == "running" and event == "fail")
    branch_running_other = (
        state == "running"
        and not branch_running_stop
        and not branch_running_fail
    )

    # Branch: failed state transitions
    branch_failed_reset = (state == "failed" and event == "reset")
    branch_failed_other = (state == "failed" and not branch_failed_reset)

    # Branch: unknown state
    branch_unknown_state = (
        not branch_idle_start
        and not branch_idle_other
        and not branch_running_stop
        and not branch_running_fail
        and not branch_running_other
        and not branch_failed_reset
        and not branch_failed_other
    )

    if branch_idle_start:
        return "running"
    elif branch_idle_other:
        return state
    elif branch_running_stop:
        return "idle"
    elif branch_running_fail:
        return "failed"
    elif branch_running_other:
        return state
    elif branch_failed_reset:
        return "idle"
    elif branch_failed_other:
        return state
    elif branch_unknown_state:
        return state

    # Fallback (unreachable under normal conditions)
    return state
