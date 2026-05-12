import typing

FlagDict = typing.Dict[str, bool]
SegmentConfig = typing.Dict[str, FlagDict]
UserObject = typing.Dict[str, typing.Any]


def _get_user_segments(user: UserObject) -> typing.List[str]:
    """
    Safely extracts and validates the list of segment names from the user object.
    """
    user_segments = user.get("segments", [])

    if not isinstance(user_segments, list):
        raise TypeError("The 'segments' field in the user object must be a list.")

    for segment_name in user_segments:
        if not isinstance(segment_name, str):
            raise TypeError(
                "All items in the user 'segments' list must be strings."
            )

    return user_segments


def _get_user_overrides(user: UserObject) -> FlagDict:
    """
    Safely extracts and validates the flag overrides from the user object.
    """
    user_overrides = user.get("overrides", {})

    if not isinstance(user_overrides, dict):
        raise TypeError(
            "The 'overrides' field in the user object must be a dictionary."
        )

    return user_overrides


def resolve_flags(
    defaults: FlagDict,
    segments: SegmentConfig,
    user: UserObject,
) -> FlagDict:
    """
    Resolves feature flags for a user based on a matrix of configurations.

    The resolution follows a clear precedence order, with later steps
    overwriting earlier ones:
    1. Base default values.
    2. Overrides from each of the user's segments, applied in the order
       they are listed.
    3. User-specific overrides.

    This function does not mutate any of the input dictionaries.

    Args:
        defaults: A dictionary of default flag values.
        segments: A dictionary mapping segment names to flag override dictionaries.
        user: An object representing the user, which may contain 'segments' (a list
              of strings) and 'overrides' (a dictionary of flags).

    Returns:
        A new dictionary containing the resolved feature flags.

    Raises:
        TypeError: If inputs or their nested structures have incorrect types.
    """
    if not isinstance(defaults, dict):
        raise TypeError("'defaults' must be a dictionary.")
    if not isinstance(segments, dict):
        raise TypeError("'segments' must be a dictionary.")
    if not isinstance(user, dict):
        raise TypeError("'user' must be a dictionary.")

    resolved_flags = defaults.copy()

    user_segment_names = _get_user_segments(user)
    for segment_name in user_segment_names:
        segment_overrides = segments.get(segment_name)

        if segment_overrides is None:
            continue

        if not isinstance(segment_overrides, dict):
            raise TypeError(
                f"Configuration for segment '{segment_name}' must be a dictionary."
            )

        resolved_flags.update(segment_overrides)

    user_overrides = _get_user_overrides(user)
    resolved_flags.update(user_overrides)

    return resolved_flags
