"""
A module for resolving feature flags based on user context.
"""

from typing import Dict, List, Any


def resolve_flags(
    defaults: Dict[str, bool],
    segments: Dict[str, Dict[str, bool]],
    user: Dict[str, Any],
) -> Dict[str, bool]:
    """
    Resolves feature flags for a user based on defaults, segments, and overrides.

    The resolution follows a specific order of precedence:
    1. Default values are the base.
    2. Segment overrides are applied in the order they appear in the user's
       segment list. Unknown segments are ignored.
    3. User-specific overrides are applied last and have the highest precedence.

    Args:
        defaults: A dictionary of default flag values.
        segments: A dictionary where keys are segment names and values are
                  dictionaries of flag overrides for that segment.
        user: A dictionary representing the user context. It may contain:
              - "segments": A list of segment names the user belongs to.
              - "overrides": A dictionary of user-specific flag overrides.

    Returns:
        A new dictionary with the final resolved flag values for the user.
        The input dictionaries are not mutated.
    """
    # Start with a copy of the defaults to avoid mutating the input dictionary.
    resolved_flags = defaults.copy()

    # Apply segment overrides in the order listed for the user.
    user_segments = user.get("segments")
    if isinstance(user_segments, list):
        for segment_name in user_segments:
            if segment_name in segments:
                resolved_flags.update(segments[segment_name])

    # Apply user-specific overrides, which have the highest precedence.
    user_overrides = user.get("overrides")
    if isinstance(user_overrides, dict):
        resolved_flags.update(user_overrides)

    return resolved_flags
