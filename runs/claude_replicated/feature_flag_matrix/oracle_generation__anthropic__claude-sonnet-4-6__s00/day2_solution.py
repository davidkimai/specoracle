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
      - ``"default"``            – value comes from *defaults*
      - ``"segment:<name>"``     – value was last set by a segment override
      - ``"user_override"``      – value was last set by user["overrides"]

    Precedence and unknown-segment rules are identical to :func:`resolve_flags`.
    Inputs are never mutated.
    """
    # Track value and source for every flag encountered.
    result: dict[str, dict] = {}

    for flag, value in defaults.items():
        result[flag] = {"value": value, "source": "default"}

    for segment_name in user.get("segments", []):
        segment_flags = segments.get(segment_name)
        if segment_flags is None:
            continue
        for flag, value in segment_flags.items():
            result[flag] = {"value": value, "source": f"segment:{segment_name}"}

    user_overrides = user.get("overrides")
    if user_overrides is not None:
        for flag, value in user_overrides.items():
            result[flag] = {"value": value, "source": "user_override"}

    return result
