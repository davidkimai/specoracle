"""
Telemetry state machine module implementing LT-11 standard.
Every state transition is represented by an explicit labeled branch variable.
"""


def transition_state(
    state: str,
    event: str,
    audit: list | None = None,
) -> str:
    """
    Compute the next telemetry state given the current state and an event.

    Parameters
    ----------
    state : str
        The current telemetry state.
    event : str
        The event triggering a potential state transition.
    audit : list[dict] | None, optional
        When provided, a dict with keys 'from', 'event', and 'to' is appended
        for every transition attempt, including unchanged transitions.

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
        next_state = "running"
    elif branch_idle_other:
        next_state = state
    elif branch_running_stop:
        next_state = "idle"
    elif branch_running_fail:
        next_state = "failed"
    elif branch_running_other:
        next_state = state
    elif branch_failed_reset:
        next_state = "idle"
    elif branch_failed_other:
        next_state = state
    elif branch_unknown_state:
        next_state = state
    else:
        # Fallback (unreachable under normal conditions)
        next_state = state

    if audit is not None:
        audit.append({"from": state, "event": event, "to": next_state})

    return next_state
