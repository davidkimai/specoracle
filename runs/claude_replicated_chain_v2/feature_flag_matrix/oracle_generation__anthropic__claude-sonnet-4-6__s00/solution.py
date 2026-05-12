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
    """Return resolved feature flags for *user*.

    Precedence (lowest → highest):
      1. defaults
      2. segment overrides, applied in the order listed in user["segments"]
      3. user["overrides"]

    Unknown segment names are silently skipped.
    Inputs are never mutated.
    """
    flags = dict(defaults)

    for segment_name in user.get("segments", []):
        segment_flags = segments.get(segment_name)
        if segment_flags is not None:
            flags.update(segment_flags)

    user_overrides = user.get("overrides")
    if user_overrides is not None:
        flags.update(user_overrides)

    return flags
