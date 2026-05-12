"""
Resolves feature flags based on a matrix of defaults, segments, and user overrides.
"""

import typing


def resolve_flags(
    defaults: typing.Dict[str, bool],
    segments: typing.Dict[str, typing.Dict[str, bool]],
    user: typing.Dict[str, typing.Any],
) -> typing.Dict[str, bool]:
    """
    Calculates the final feature flag values for a user.

    The resolution process follows a specific order of precedence:
    1. Base values are taken from the `defaults` dictionary.
    2. Overrides from each of the user's `segments` are applied in order.
    3. User-specific `overrides` are applied last, having the highest precedence.

    This function does not mutate any of the input dictionaries.

    Args:
        defaults: A dictionary of default flag values.
        segments: A dictionary mapping segment names to flag override dictionaries.
        user: A dictionary containing user information. It may include:
              - 'segments': A list of segment names the user belongs to.
              - 'overrides': A dictionary of user-specific flag overrides.

    Returns:
        A new dictionary containing the resolved feature flags for the user.

    Raises:
        TypeError: If `user['segments']` is present but not a list, or if
                   `user['overrides']` is present but not a dictionary.
    """
    # Start with a copy of the defaults to ensure inputs are not mutated.
    resolved_flags = defaults.copy()

    # Apply segment overrides in the order they are listed for the user.
    user_segments = user.get("segments", [])
    if not isinstance(user_segments, list):
        raise TypeError(
            f"user['segments'] must be a list, but found "
            f"{type(user_segments).__name__}."
        )

    for segment_name in user_segments:
        # Per requirements, ignore segments that are not defined.
        segment_overrides = segments.get(segment_name)
        if segment_overrides is not None:
            resolved_flags.update(segment_overrides)

    # Apply user-specific overrides, which have the highest precedence.
    user_overrides = user.get("overrides", {})
    if not isinstance(user_overrides, dict):
        raise TypeError(
            f"user['overrides'] must be a dictionary, but found "
            f"{type(user_overrides).__name__}."
        )

    resolved_flags.update(user_overrides)

    return resolved_flags
