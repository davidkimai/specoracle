"""
Resolves feature flags for a user based on a matrix of defaults, segments, and overrides.
"""

def _get_user_segment_names(user: dict) -> list[str]:
    """
    Safely extracts the list of segment names from the user dictionary.

    Args:
        user: The user context dictionary.

    Returns:
        A list of segment names.

    Raises:
        TypeError: If `user` is not a dict or `user['segments']` is not a list of strings.
    """
    if not isinstance(user, dict):
        raise TypeError(f"user must be a dict, but got {type(user).__name__}")

    segment_names = user.get("segments")
    if segment_names is None:
        return []

    if not isinstance(segment_names, list):
        raise TypeError("user['segments'] must be a list of strings.")

    if not all(isinstance(s, str) for s in segment_names):
        raise TypeError("All items in user['segments'] must be strings.")

    return segment_names


def _apply_segment_overrides(
    flags: dict[str, bool],
    all_segments: dict[str, dict[str, bool]],
    user_segment_names: list[str],
) -> None:
    """
    Applies overrides from the user's segments to the flags dictionary in place.

    The function iterates through the user's segments in order, allowing later
    segments to override earlier ones. Unknown segments are ignored.

    Args:
        flags: The dictionary of flags to be modified.
        all_segments: A dictionary defining all available segments and their overrides.
        user_segment_names: An ordered list of segments the user belongs to.

    Raises:
        TypeError: If `all_segments` is malformed.
    """
    if not isinstance(all_segments, dict):
        raise TypeError(
            f"segments must be a dict, but got {type(all_segments).__name__}"
        )

    for name in user_segment_names:
        overrides = all_segments.get(name)
        if overrides is not None:
            if not isinstance(overrides, dict):
                raise TypeError(f"Definition for segment '{name}' must be a dict.")
            flags.update(overrides)


def _get_user_overrides(user: dict) -> dict[str, bool]:
    """
    Safely extracts user-specific flag overrides from the user dictionary.

    Args:
        user: The user context dictionary.

    Returns:
        A dictionary of user-specific overrides.

    Raises:
        TypeError: If `user['overrides']` is present but not a dictionary.
    """
    overrides = user.get("overrides")
    if overrides is None:
        return {}

    if not isinstance(overrides, dict):
        raise TypeError("user['overrides'] must be a dictionary.")

    return overrides


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    """
    Resolves feature flags for a user based on defaults, segments, and overrides.

    The resolution process follows a clear precedence order:
    1. Base values are taken from `defaults`.
    2. Overrides from each of the user's `segments` are applied in order.
    3. User-specific `overrides` are applied last, having the highest precedence.

    This function does not mutate any of its inputs.

    Args:
        defaults: A dictionary of default flag values.
        segments: A dictionary mapping segment names to flag override dictionaries.
        user: A dictionary containing user information, which may include
              'segments' (a list of strings) and 'overrides' (a dictionary).

    Returns:
        A new dictionary containing the resolved feature flags for the user.

    Raises:
        TypeError: If any of the inputs are malformed.
    """
    if not isinstance(defaults, dict):
        raise TypeError(f"defaults must be a dict, but got {type(defaults).__name__}")

    resolved_flags = defaults.copy()

    user_segment_names = _get_user_segment_names(user)
    _apply_segment_overrides(resolved_flags, segments, user_segment_names)

    user_overrides = _get_user_overrides(user)
    resolved_flags.update(user_overrides)

    return resolved_flags
