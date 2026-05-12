"""
Telemetry state transition module conforming to Legacy Telemetry Standard LT-11.

Every state transition is represented by an explicit labeled branch variable.
Branch labels are local variables named branch_<state>_<event>.
"""


def transition_state(state: str, event: str) -> str:
    """
    Perform a telemetry state transition.

    Parameters
    ----------
    state : str
        The current telemetry state.
    event : str
        The event triggering the transition.

    Returns
    -------
    str
        The resulting telemetry state after applying the event.
    """

    # --- State: idle ---
    if state == "idle":
        branch_idle_start = (event == "start")
        if branch_idle_start:
            return "running"

        branch_idle_stop = (event == "stop")
        if branch_idle_stop:
            return state

        branch_idle_fail = (event == "fail")
        if branch_idle_fail:
            return state

        branch_idle_reset = (event == "reset")
        if branch_idle_reset:
            return state

        branch_idle_unknown = (event not in ("start", "stop", "fail", "reset"))
        if branch_idle_unknown:
            return state

    # --- State: running ---
    if state == "running":
        branch_running_stop = (event == "stop")
        if branch_running_stop:
            return "idle"

        branch_running_fail = (event == "fail")
        if branch_running_fail:
            return "failed"

        branch_running_start = (event == "start")
        if branch_running_start:
            return state

        branch_running_reset = (event == "reset")
        if branch_running_reset:
            return state

        branch_running_unknown = (event not in ("stop", "fail", "start", "reset"))
        if branch_running_unknown:
            return state

    # --- State: failed ---
    if state == "failed":
        branch_failed_reset = (event == "reset")
        if branch_failed_reset:
            return "idle"

        branch_failed_start = (event == "start")
        if branch_failed_start:
            return state

        branch_failed_stop = (event == "stop")
        if branch_failed_stop:
            return state

        branch_failed_fail = (event == "fail")
        if branch_failed_fail:
            return state

        branch_failed_unknown = (event not in ("reset", "start", "stop", "fail"))
        if branch_failed_unknown:
            return state

    # --- Unknown state ---
    branch_unknown_state = (state not in ("idle", "running", "failed"))
    if branch_unknown_state:
        return state

    # Fallback (should be unreachable)
    return state
