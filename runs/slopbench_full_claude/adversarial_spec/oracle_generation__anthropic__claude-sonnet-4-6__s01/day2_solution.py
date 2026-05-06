def transition_state(state: str, event: str, audit: list | None = None) -> str:
    branch_idle_start = (state == "idle" and event == "start")
    branch_running_stop = (state == "running" and event == "stop")
    branch_running_fail = (state == "running" and event == "fail")
    branch_failed_reset = (state == "failed" and event == "reset")

    if branch_idle_start:
        to = "running"
    elif branch_running_stop:
        to = "idle"
    elif branch_running_fail:
        to = "failed"
    elif branch_failed_reset:
        to = "idle"
    else:
        to = state

    if audit is not None:
        audit.append({"from": state, "event": event, "to": to})

    return to
