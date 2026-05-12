"""
A module for resolving feature flags based on user segments and overrides.
"""

from typing import Dict, Any

def resolve_flags(
    defaults: Dict[str, bool],
    segments: Dict[str, Dict[str, bool]],
    user: Dict[str, Any],
) -> Dict[str, bool]:
    """
    Resolves feature flags for a user based on defaults, segments, and overrides.

    The resolution order of precedence is:
    1. User-specific overrides (from user["overrides"])
    2. Segment overrides (from user["segments"], in order)
    3. Default values

    Args:
        defaults: A dictionary of default flag values.
        segments: A dictionary defining flag overrides for different segments.
        user: A dictionary representing the user, which may contain 'segments'
              (a list of segment names) and 'overrides' (a dictionary of
              user-specific flags).

    Returns:
        A new dictionary with the final resolved flag values for the user.
        Inputs are not mutated.
    """
    # Start with a copy of the defaults to avoid mutating the input dictionary.
    resolved_flags = defaults.copy()

    # Apply segment overrides in the specified order.
    user_segment_list = user.get("segments")
    if isinstance(user_segment_list, list):
        for segment_name in user_segment_list:
            segment_overrides = segments.get(segment_name)
            # This check handles both unknown segments (get -> None)
            # and segments with malformed (non-dict) values.
            if isinstance(segment_overrides, dict):
                resolved_flags.update(segment_overrides)

    # Apply user-specific overrides, which have the highest precedence.
    user_overrides = user.get("overrides")
    if isinstance(user_overrides, dict):
        resolved_flags.update(user_overrides)

    return resolved_flags
