import typing

def resolve_flags(
    defaults: typing.Dict[str, bool],
    segments: typing.Dict[str, typing.Dict[str, bool]],
    user: typing.Dict[str, typing.Any],
) -> typing.Dict[str, bool]:
    """
    Resolves feature flags for a user based on defaults, segments, and overrides.

    The resolution follows a specific order of precedence:
    1. Base values are taken from `defaults`.
    2. Overrides from segments listed in `user['segments']` are applied in order.
    3. User-specific overrides from `user['overrides']` are applied last.

    Args:
        defaults: A dictionary mapping feature flag names to their default boolean values.
        segments: A dictionary where keys are segment names and values are dictionaries
                  of flag overrides for that segment.
        user: A dictionary representing the user. It may contain:
              - "segments": A list of segment names the user belongs to.
              - "overrides": A dictionary of flag overrides specific to the user.

    Returns:
        A new dictionary containing the final resolved feature flags for the user.
        This function does not mutate any of the input dictionaries.
    """
    # Start with a copy of the defaults to ensure the original is not mutated.
    resolved_flags = defaults.copy()

    # Apply segment overrides in the order they are listed on the user.
    # Unknown segments are ignored.
    user_segments = user.get("segments", [])
    if isinstance(user_segments, list):
        for segment_name in user_segments:
            if segment_name in segments:
                resolved_flags.update(segments[segment_name])

    # Apply user-specific overrides, which have the highest precedence.
    user_overrides = user.get("overrides", {})
    if isinstance(user_overrides, dict):
        resolved_flags.update(user_overrides)

    return resolved_flags
