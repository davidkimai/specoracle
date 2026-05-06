"""
feature_flag_matrix.py

Resolve feature flags for a user given defaults, segment overrides, and
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
    """
    flags = dict(defaults)

    for segment_name in user.get("segments", []):
        if segment_name not in segments:
            continue
        flags.update(segments[segment_name])

    flags.update(user.get("overrides", {}))

    return flags
