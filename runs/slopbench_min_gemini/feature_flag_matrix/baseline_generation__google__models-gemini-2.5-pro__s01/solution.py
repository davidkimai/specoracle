"""
Resolves feature flags based on user attributes.
"""

import collections.abc
from typing import Any

def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict[str, Any],
) -> dict[str, bool]:
    """
    Resolves feature flags for a user based on defaults, segments, and overrides.

    The resolution order of precedence, from lowest to highest, is:
    1. The base `defaults`.
    2. Overrides from each segment the user belongs to, applied in the order
       listed in the user's segment list.
    3. User-specific overrides.

    Args:
        defaults: A dictionary of default flag names to their boolean values.
        segments: A dictionary mapping segment names to flag override dictionaries.
        user: A dictionary representing the user. It may contain:
              - "segments": A list of segment names the user belongs to.
              - "overrides": A dictionary of flag values specific to the user.

    Returns:
        A new dictionary with the resolved feature flags for the user.
        This function does not mutate any of the input dictionaries.
    """
    # Start with a copy of the defaults to ensure the original is not mutated.
    resolved_flags = defaults.copy()

    # Apply segment overrides in the order they appear for the user.
    user_segment_names = user.get("segments")
    if isinstance(user_segment_names, collections.abc.Sequence) and not isinstance(
        user_segment_names, str
    ):
        for segment_name in user_segment_names:
            segment_overrides = segments.get(segment_name)
            if segment_overrides:
                resolved_flags.update(segment_overrides)

    # Apply user-specific overrides, which have the highest precedence.
    user_overrides = user.get("overrides")
    if isinstance(user_overrides, dict):
        resolved_flags.update(user_overrides)

    return resolved_flags
