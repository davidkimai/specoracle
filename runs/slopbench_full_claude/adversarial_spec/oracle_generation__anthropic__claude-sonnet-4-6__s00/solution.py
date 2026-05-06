def transition_state(state: str, event: str) -> str:
    branch_idle_start = (state == "idle" and event == "start")
    branch_idle_stop = (state == "idle" and event == "stop")
    branch_idle_fail = (state == "idle" and event == "fail")
    branch_idle_reset = (state == "idle" and event == "reset")

    branch_running_start = (state == "running" and event == "start")
    branch_running_stop = (state == "running" and event == "stop")
    branch_running_fail = (state == "running" and event == "fail")
    branch_running_reset = (state == "running" and event == "reset")

    branch_failed_start = (state == "failed" and event == "start")
    branch_failed_stop = (state == "failed" and event == "stop")
    branch_failed_fail = (state == "failed" and event == "fail")
    branch_failed_reset = (state == "failed" and event == "reset")

    if branch_idle_start:
        return "running"
    elif branch_idle_stop:
        return state
    elif branch_idle_fail:
        return state
    elif branch_idle_reset:
        return state
    elif branch_running_start:
        return state
    elif branch_running_stop:
        return "idle"
    elif branch_running_fail:
        return "failed"
    elif branch_running_reset:
        return state
    elif branch_failed_start:
        return state
    elif branch_failed_stop:
        return state
    elif branch_failed_fail:
        return state
    elif branch_failed_reset:
        return "idle"
    else:
        return state
