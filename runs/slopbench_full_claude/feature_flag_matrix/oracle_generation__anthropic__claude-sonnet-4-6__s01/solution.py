"""
feature_flag_matrix.py

Resolve feature flags for a user by layering defaults, segment overrides,
and per-user overrides.
"""


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    """
    Build a feature-flag mapping for *user*.

    Resolution order (later layers win):
        1. defaults
        2. segment overrides, applied in the order listed in user["segments"]
        3. user["overrides"]

    Unknown segment names are silently skipped.
    Inputs are never mutated.
    """
    flags = dict(defaults)

    for segment_name in user.get("segments", []):
        if segment_name in segments:
            flags.update(segments[segment_name])

    flags.update(user.get("overrides", {}))

    return flags
