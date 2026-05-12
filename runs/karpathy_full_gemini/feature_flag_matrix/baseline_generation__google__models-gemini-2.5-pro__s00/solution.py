"""
A module for resolving feature flags based on user segments and overrides.
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
    1. Default flag values.
    2. Overrides from user segments, applied in the order they appear in the user's
       segment list. Later segments in the list override earlier ones.
    3. User-specific overrides.

    Args:
        defaults: A dictionary of default feature flag names to their boolean values.
        segments: A dictionary where keys are segment names and values are
                  dictionaries of flag overrides for that segment.
        user: A dictionary representing the user. It may contain:
              - "segments": A list of segment names (str) the user belongs to.
              - "overrides": A dictionary of flag names (str) to boolean values
                             that are specific to this user.

    Returns:
        A new dictionary containing the final resolved feature flags for the user.
        The input dictionaries are not mutated.
    """
    # Start with a copy of the defaults to avoid mutating the input.
    resolved = defaults.copy()

    # Apply segment overrides in the specified order.
    user_segments: List[str] = user.get("segments", [])
    if isinstance(user_segments, list):
        for segment_name in user_segments:
            if segment_name in segments:
                segment_overrides = segments[segment_name]
                if isinstance(segment_overrides, dict):
                    resolved.update(segment_overrides)

    # Apply user-specific overrides, which have the highest precedence.
    user_overrides: Dict[str, bool] = user.get("overrides", {})
    if isinstance(user_overrides, dict):
        resolved.update(user_overrides)

    return resolved
