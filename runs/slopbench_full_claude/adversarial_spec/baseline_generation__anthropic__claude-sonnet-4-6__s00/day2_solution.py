def transition_state(state: str, event: str, audit: list | None = None) -> str:
    transitions = {
        ("idle", "start"): "running",
        ("running", "stop"): "idle",
        ("running", "fail"): "failed",
        ("failed", "reset"): "idle",
    }
    to = transitions.get((state, event), state)
    if audit is not None:
        audit.append({"from": state, "event": event, "to": to})
    return to
