# feature_flag_matrix.py

from typing import Any, Dict


def resolve_flags(
    defaults: Dict[str, bool],
    segments: Dict[str, Dict[str, bool]],
    user: Dict[str, Any],
) -> Dict[str, bool]:
    """Resolves feature flags based on defaults, segments, and user overrides.

    The resolution follows a specific order of precedence:
    1. Default values are used as the base.
    2. Overrides from segments listed in the user profile are applied in order.
    3. User-specific overrides are applied last, having the highest precedence.

    Args:
        defaults: A dictionary mapping feature flag names to their default
                  boolean values.
        segments: A dictionary where keys are segment names and values are
                  dictionaries of flag overrides for that segment.
        user: A dictionary representing the user. It may contain:
              - "segments": A list of segment names the user belongs to.
              - "overrides": A dictionary of flag overrides specific to this user.

    Returns:
        A new dictionary containing the final resolved feature flag values for
        the user. The input dictionaries are not mutated.
    """
    resolved = defaults.copy()

    # Apply segment overrides in the order specified for the user.
    # Unknown segments are ignored.
    for segment_name in user.get("segments", []):
        if segment_name in segments:
            resolved.update(segments[segment_name])

    # Apply user-specific overrides, which have the highest precedence.
    resolved.update(user.get("overrides", {}))

    return resolved
