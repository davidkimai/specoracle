def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    """
    Resolve feature flags for a user.

    Resolution order:
    1. Start with default flags.
    2. Apply segment overrides in the order listed in user["segments"].
       Unknown segments are ignored.
    3. Apply user["overrides"] if present.

    Inputs are not mutated.
    """
    resolved = dict(defaults)

    for segment_name in user.get("segments", []):
        segment_overrides = segments.get(segment_name)
        if segment_overrides is not None:
            resolved.update(segment_overrides)

    if "overrides" in user:
        resolved.update(user["overrides"])

    return resolved
