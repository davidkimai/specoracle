"""
feature_flag_matrix.py

Resolves feature flags for a user given defaults, segment overrides, and
per-user overrides.
"""


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    """Return resolved feature flags for *user*.

    Resolution order (later entries win):
    1. defaults
    2. segment overrides, applied in the order listed in user["segments"]
    3. user["overrides"]

    Unknown segment names are silently ignored.
    Inputs are never mutated.
    """
    flags = dict(defaults)

    for segment_name in user.get("segments", []):
        segment_overrides = segments.get(segment_name)
        if segment_overrides is None:
            continue
        flags.update(segment_overrides)

    flags.update(user.get("overrides", {}))

    return flags
