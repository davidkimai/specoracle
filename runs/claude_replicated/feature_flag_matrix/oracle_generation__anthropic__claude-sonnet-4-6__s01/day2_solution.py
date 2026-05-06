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


def explain_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, dict]:
    """Return each final flag value with the source that last changed it.

    Each entry has the form::

        {"flag_name": {"value": bool, "source": str}}

    where *source* is one of:

    * ``"default"`` – the value came from *defaults* and was never overridden
    * ``"segment:<name>"`` – the value was last set by the named segment
    * ``"user_override"`` – the value was set by ``user["overrides"]``
    """
    # Track value and source together; resolution order mirrors resolve_flags.
    result: dict[str, dict] = {}

    # 1. Defaults
    for flag, value in defaults.items():
        result[flag] = {"value": value, "source": "default"}

    # 2. Segment overrides in listed order
    for segment_name in user.get("segments", []):
        if segment_name not in segments:
            continue
        for flag, value in segments[segment_name].items():
            result[flag] = {"value": value, "source": f"segment:{segment_name}"}

    # 3. Per-user overrides
    for flag, value in user.get("overrides", {}).items():
        result[flag] = {"value": value, "source": "user_override"}

    return result
