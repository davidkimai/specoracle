def transition_state(state: str, event: str) -> str:
    branch_idle_start = (state == "idle" and event == "start")
    branch_running_stop = (state == "running" and event == "stop")
    branch_running_fail = (state == "running" and event == "fail")
    branch_failed_reset = (state == "failed" and event == "reset")

    if branch_idle_start:
        return "running"
    if branch_running_stop:
        return "idle"
    if branch_running_fail:
        return "failed"
    if branch_failed_reset:
        return "idle"
    return state
