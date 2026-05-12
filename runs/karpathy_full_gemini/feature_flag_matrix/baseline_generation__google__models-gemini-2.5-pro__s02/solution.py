# This is a generated file. DO NOT EDIT.
"""
This module provides functionality for resolving feature flags based on user segments and overrides.
"""

import typing

def resolve_flags(
    defaults: typing.Dict[str, bool],
    segments: typing.Dict[str, typing.Dict[str, bool]],
    user: typing.Dict[str, typing.Any],
) -> typing.Dict[str, bool]:
    """
    Resolves feature flags for a given user.

    The resolution process follows a specific order of precedence:
    1. Base values are taken from the `defaults` dictionary.
    2. Overrides from segments listed in `user['segments']` are applied in order.
       If a segment name from the user list is not found in the `segments`
       dictionary, it is ignored.
    3. Specific user overrides from `user['overrides']` are applied last,
       having the highest precedence.

    Args:
        defaults: A dictionary of default flag values.
        segments: A dictionary mapping segment names to their flag overrides.
        user: A dictionary representing the user, which may contain 'segments'
              (a list of strings) and/or 'overrides' (a dictionary of
              string to boolean).

    Returns:
        A new dictionary with the resolved feature flags for the user.
        The input dictionaries are not mutated.
    """
    # Start with a copy of the defaults to ensure the original is not mutated.
    resolved_flags = defaults.copy()

    # Apply segment overrides in the order they are listed for the user.
    user_segments = user.get("segments", [])
    if isinstance(user_segments, list):
        for segment_name in user_segments:
            # Ignore segments that are not defined.
            if segment_name in segments:
                segment_overrides = segments[segment_name]
                if isinstance(segment_overrides, dict):
                    resolved_flags.update(segment_overrides)

    # Apply user-specific overrides, which have the highest precedence.
    user_overrides = user.get("overrides", {})
    if isinstance(user_overrides, dict):
        resolved_flags.update(user_overrides)

    return resolved_flags
