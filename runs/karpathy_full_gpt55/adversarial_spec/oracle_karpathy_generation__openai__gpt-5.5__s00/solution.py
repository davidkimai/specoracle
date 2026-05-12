def transition_state(state: str, event: str) -> str:
    branch_idle_start = state == "idle" and event == "start"
    if branch_idle_start:
        return "running"

    branch_running_stop = state == "running" and event == "stop"
    if branch_running_stop:
        return "idle"

    branch_running_fail = state == "running" and event == "fail"
    if branch_running_fail:
        return "failed"

    branch_failed_reset = state == "failed" and event == "reset"
    if branch_failed_reset:
        return "idle"

    return state
