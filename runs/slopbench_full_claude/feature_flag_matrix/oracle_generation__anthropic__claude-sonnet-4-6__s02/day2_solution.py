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

    Possible source values:
    * ``"default"``            – flag was only set in *defaults*
    * ``"segment:<name>"``     – last changed by the named segment override
    * ``"user_override"``      – last changed by ``user["overrides"]``

    Resolution order matches :func:`resolve_flags` (later entries win).
    Unknown segment names are silently ignored.
    Inputs are never mutated.
    """
    # Track value and source together; start from defaults.
    result: dict[str, dict] = {
        flag: {"value": value, "source": "default"}
        for flag, value in defaults.items()
    }

    for segment_name in user.get("segments", []):
        segment_overrides = segments.get(segment_name)
        if segment_overrides is None:
            continue
        source = f"segment:{segment_name}"
        for flag, value in segment_overrides.items():
            result[flag] = {"value": value, "source": source}

    for flag, value in user.get("overrides", {}).items():
        result[flag] = {"value": value, "source": "user_override"}

    return result
