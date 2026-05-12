"""
A module for resolving feature flags based on a hierarchy of configurations.
"""

def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    """
    Resolves feature flags for a user based on defaults, segments, and overrides.

    The resolution follows a specific order of precedence:
    1. Default values are the base.
    2. Segment overrides are applied in the order they appear in the user's
       segment list. Later segments in the list can override earlier ones.
    3. User-specific overrides are applied last and have the highest precedence.

    Args:
        defaults: A dictionary of default flag values.
        segments: A dictionary where keys are segment names and values are
                  dictionaries of flag overrides for that segment.
        user: A dictionary representing the user. It may contain:
              - "segments": A list of segment names the user belongs to.
              - "overrides": A dictionary of flag overrides specific to this user.

    Returns:
        A new dictionary containing the final resolved flag values for the user.
        The input dictionaries are not mutated.
    """
    # 1. Start with a copy of the defaults to ensure inputs are not mutated.
    resolved_flags = defaults.copy()

    # 2. Apply segment overrides.
    # We use .get() to safely access keys that may not exist.
    user_segments = user.get("segments")
    if isinstance(user_segments, list):
        for segment_name in user_segments:
            # Look up the segment's overrides, ignoring unknown segments.
            segment_overrides = segments.get(segment_name)
            if isinstance(segment_overrides, dict):
                # Apply the overrides. Flags from later segments in the list
                # will overwrite those from earlier ones.
                resolved_flags.update(segment_overrides)

    # 3. Apply user-specific overrides, which have the highest precedence.
    user_overrides = user.get("overrides")
    if isinstance(user_overrides, dict):
        resolved_flags.update(user_overrides)

    return resolved_flags
