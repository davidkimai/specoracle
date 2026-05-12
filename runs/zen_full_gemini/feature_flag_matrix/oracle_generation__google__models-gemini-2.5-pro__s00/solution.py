"""
Resolves feature flags for a user based on a matrix of defaults, segments, and overrides.
"""

import typing


def _apply_segment_overrides(
    flags_to_update: dict[str, bool],
    all_segments: dict[str, dict[str, bool]],
    user: dict,
) -> None:
    """
    Applies segment-based flag overrides to a flag dictionary in place.

    Iterates through the segments listed in user['segments'], applying overrides
    for each known segment in order.

    Args:
        flags_to_update: The dictionary of flags to be modified.
        all_segments: A dictionary containing all available segment definitions.
        user: The user dictionary, which may contain a 'segments' list.

    Raises:
        TypeError: If user['segments'] is present but is not a list.
    """
    user_segment_names = user.get("segments", [])

    if not isinstance(user_segment_names, list):
        raise TypeError("user['segments'] must be a list of segment names.")

    for segment_name in user_segment_names:
        # Per requirements, unknown segments are ignored.
        # .get() gracefully handles cases where a segment_name is not found.
        segment_overrides = all_segments.get(segment_name)
        if isinstance(segment_overrides, dict):
            flags_to_update.update(segment_overrides)


def _apply_user_overrides(
    flags_to_update: dict[str, bool],
    user: dict,
) -> None:
    """
    Applies user-specific flag overrides to a flag dictionary in place.

    Args:
        flags_to_update: The dictionary of flags to be modified.
        user: The user dictionary, which may contain an 'overrides' dictionary.

    Raises:
        TypeError: If user['overrides'] is present but is not a dictionary.
    """
    user_overrides = user.get("overrides", {})

    if not isinstance(user_overrides, dict):
        raise TypeError("user['overrides'] must be a dictionary.")

    flags_to_update.update(user_overrides)


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    """
    Resolves feature flags for a user based on defaults, segments, and overrides.

    The resolution follows a clear precedence:
    1. Base defaults are applied first.
    2. Segment overrides are applied in the order they appear in the user's
       segment list. Later segments in the list override earlier ones.
    3. User-specific overrides are applied last, taking the highest precedence.

    This function does not mutate any of the input dictionaries.

    Args:
        defaults: A dictionary of default flag values.
        segments: A dictionary mapping segment names to flag override dictionaries.
        user: A dictionary representing the user context, which may contain
              'segments' (a list of strings) and 'overrides' (a dictionary).

    Returns:
        A new dictionary with the final resolved feature flags for the user.

    Raises:
        TypeError: If the structure of the 'user' dictionary is invalid
                   (e.g., 'segments' is not a list or 'overrides' is not a dict).
    """
    # Start with a copy of the defaults to avoid mutating the input dictionary.
    # This also establishes the base set of flags.
    resolved_flags = defaults.copy()

    # Apply segment overrides in the order specified for the user.
    _apply_segment_overrides(resolved_flags, segments, user)

    # Apply user-specific overrides, which have the highest precedence.
    _apply_user_overrides(resolved_flags, user)

    return resolved_flags
