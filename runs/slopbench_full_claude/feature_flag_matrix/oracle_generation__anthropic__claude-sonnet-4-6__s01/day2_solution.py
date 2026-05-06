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


def explain_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, dict]:
    """
    Return each final flag value together with the source that last set it.

    Return format::

        {
            "flag_name": {"value": bool, "source": str},
            ...
        }

    Possible source strings:
        * ``"default"``            – value comes from *defaults*
        * ``"segment:<name>"``     – value last set by the named segment
        * ``"user_override"``      – value set by user["overrides"]

    Resolution order is identical to :func:`resolve_flags`.
    Inputs are never mutated.
    """
    # Track value and source for every flag we encounter.
    result: dict[str, dict] = {}

    # Layer 1: defaults
    for flag, value in defaults.items():
        result[flag] = {"value": value, "source": "default"}

    # Layer 2: segment overrides in user-specified order
    for segment_name in user.get("segments", []):
        if segment_name in segments:
            for flag, value in segments[segment_name].items():
                result[flag] = {"value": value, "source": f"segment:{segment_name}"}

    # Layer 3: per-user overrides
    for flag, value in user.get("overrides", {}).items():
        result[flag] = {"value": value, "source": "user_override"}

    return result
