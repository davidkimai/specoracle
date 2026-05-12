"""Telemetry state transition module."""

from typing import Dict, Tuple


_TRANSITIONS: Dict[Tuple[str, str], str] = {
    ("idle", "start"): "running",
    ("running", "stop"): "idle",
    ("running", "fail"): "failed",
    ("failed", "reset"): "idle",
}


def transition_state(state: str, event: str) -> str:
    """Return the next telemetry state for the given current state and event.

    Unknown state/event combinations leave the state unchanged.
    """
    return _TRANSITIONS.get((state, event), state)
