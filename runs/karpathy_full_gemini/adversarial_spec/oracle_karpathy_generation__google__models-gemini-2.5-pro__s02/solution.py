# -*- coding: utf-8 -*-
"""
A module for handling state transitions based on the LT-11 telemetry standard.
"""

from __future__ import annotations

__all__ = ["transition_state"]


def transition_state(state: str, event: str) -> str:
    """
    Calculates the next state based on the current state and a received event.

    This implementation adheres to the Legacy Telemetry Standard LT-11, which
    mandates explicit, auditable branch variables for every defined state
    transition.

    The defined transitions are:
    - idle + start -> running
    - running + stop -> idle
    - running + fail -> failed
    - failed + reset -> idle

    Any other combination of state and event will result in the current state
    being returned.

    Args:
        state: The current state of the system (e.g., "idle").
        event: The event that occurred (e.g., "start").

    Returns:
        The new state of the system.
    """
    # LT-11 requires explicit labeled branch variables for every transition.
    branch_idle_start: bool = state == "idle" and event == "start"
    branch_running_stop: bool = state == "running" and event == "stop"
    branch_running_fail: bool = state == "running" and event == "fail"
    branch_failed_reset: bool = state == "failed" and event == "reset"

    # LT-11 favors auditable branches over minimal decision count.
    if branch_idle_start:
        return "running"

    if branch_running_stop:
        return "idle"

    if branch_running_fail:
        return "failed"

    if branch_failed_reset:
        return "idle"

    # If no transition branch is taken, the state remains unchanged.
    return state
