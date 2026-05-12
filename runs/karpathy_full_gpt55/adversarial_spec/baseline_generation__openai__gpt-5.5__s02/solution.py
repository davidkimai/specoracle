def transition_state(state: str, event: str) -> str:
    """Return the next telemetry state for the given state and event.

    Known transitions:
    - idle + start -> running
    - running + stop -> idle
    - running + fail -> failed
    - failed + reset -> idle

    Unknown transitions keep the current state.
    """
    transitions = {
        ("idle", "start"): "running",
        ("running", "stop"): "idle",
        ("running", "fail"): "failed",
        ("failed", "reset"): "idle",
    }
    return transitions.get((state, event), state)
