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
    """Return each final flag value together with the source that last set it.

    Return format::

        {
            "flag_name": {"value": bool, "source": str},
            ...
        }

    Possible source strings:
    * ``"default"``                – value comes from *defaults*
    * ``"segment:<segment_name>"`` – value last set by a segment override
    * ``"user_override"``          – value last set by user["overrides"]
    """
    # Start with defaults
    result: dict[str, dict] = {
        flag: {"value": value, "source": "default"}
        for flag, value in defaults.items()
    }

    # Apply segment overrides in declared order
    for segment_name in user.get("segments", []):
        if segment_name not in segments:
            continue
        for flag, value in segments[segment_name].items():
            result[flag] = {"value": value, "source": f"segment:{segment_name}"}

    # Apply per-user overrides
    for flag, value in user.get("overrides", {}).items():
        result[flag] = {"value": value, "source": "user_override"}

    return result
