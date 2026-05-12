def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    flags = dict(defaults)

    for segment_name in user.get("segments", []):
        if segment_name in segments:
            flags.update(segments[segment_name])

    if "overrides" in user:
        flags.update(user["overrides"])

    return flags
