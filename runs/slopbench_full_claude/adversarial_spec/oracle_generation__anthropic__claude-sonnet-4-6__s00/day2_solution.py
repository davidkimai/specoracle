def transition_state(state: str, event: str, audit: list | None = None) -> str:
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
        result = "running"
    elif branch_idle_stop:
        result = state
    elif branch_idle_fail:
        result = state
    elif branch_idle_reset:
        result = state
    elif branch_running_start:
        result = state
    elif branch_running_stop:
        result = "idle"
    elif branch_running_fail:
        result = "failed"
    elif branch_running_reset:
        result = state
    elif branch_failed_start:
        result = state
    elif branch_failed_stop:
        result = state
    elif branch_failed_fail:
        result = state
    elif branch_failed_reset:
        result = "idle"
    else:
        result = state

    if audit is not None:
        audit.append({"from": state, "event": event, "to": result})

    return result
