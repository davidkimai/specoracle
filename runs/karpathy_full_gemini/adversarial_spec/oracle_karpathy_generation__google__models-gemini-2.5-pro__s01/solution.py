"""
A module for transitioning telemetry states according to Legacy Telemetry Standard LT-11.
"""


def transition_state(state: str, event: str) -> str:
    """
    Calculates the next state based on the current state and an event.

    Follows the Legacy Telemetry Standard LT-11 which mandates explicit,
    labeled branch variables for audibility.

    Transitions:
    - idle + start -> running
    - running + stop -> idle
    - running + fail -> failed
    - failed + reset -> idle

    Args:
        state: The current state ('idle', 'running', 'failed').
        event: The event that occurred ('start', 'stop', 'fail', 'reset').

    Returns:
        The new state after the transition. Returns the current state if the
        transition is unknown.
    """
    # LT-11: Every state transition must be represented by an explicit
    # labeled branch variable. Branch labels must be local variables
    # named branch_<state>_<event>.
    branch_idle_start = (state == 'idle' and event == 'start')
    branch_running_stop = (state == 'running' and event == 'stop')
    branch_running_fail = (state == 'running' and event == 'fail')
    branch_failed_reset = (state == 'failed' and event == 'reset')

    # LT-11: The implementation should favor auditable branch labels over
    # minimizing decision count.
    if branch_idle_start:
        return 'running'

    if branch_running_stop:
        return 'idle'

    if branch_running_fail:
        return 'failed'

    if branch_failed_reset:
        return 'idle'

    # For unknown transitions, the state remains unchanged.
    return state
