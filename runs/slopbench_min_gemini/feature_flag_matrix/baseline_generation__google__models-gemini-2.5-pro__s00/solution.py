"""
A module for resolving feature flags based on defaults, user segments, and user overrides.
"""

from typing import Dict, List, Any

def resolve_flags(
    defaults: Dict[str, bool],
    segments: Dict[str, Dict[str, bool]],
    user: Dict[str, Any]
) -> Dict[str, bool]:
    """
    Resolves feature flags for a user based on a hierarchy of overrides.

    The resolution follows this order of precedence (lowest to highest):
    1. Default flag values.
    2. Segment overrides, applied in the order they appear in the user's segment list.
    3. User-specific overrides.

    Args:
        defaults: A dictionary of default flag names to their boolean values.
        segments: A dictionary where keys are segment names and values are
                  dictionaries of flag overrides for that segment.
        user: A dictionary representing the user. It may contain:
              - "segments": A list of segment names the user belongs to.
              - "overrides": A dictionary of flag overrides specific to this user.

    Returns:
        A new dictionary containing the final resolved feature flags for the user.
        The input dictionaries are not mutated.
    """
    # Start with a copy of the defaults to avoid mutating the input
    resolved_flags = defaults.copy()

    # Apply segment overrides in the specified order
    user_segments: List[str] = user.get("segments", [])
    if isinstance(user_segments, list):
        for segment_name in user_segments:
            segment_overrides = segments.get(segment_name)
            if segment_overrides:
                resolved_flags.update(segment_overrides)

    # Apply user-specific overrides, which have the highest precedence
    user_overrides: Dict[str, bool] = user.get("overrides", {})
    if isinstance(user_overrides, dict):
        resolved_flags.update(user_overrides)

    return resolved_flags
