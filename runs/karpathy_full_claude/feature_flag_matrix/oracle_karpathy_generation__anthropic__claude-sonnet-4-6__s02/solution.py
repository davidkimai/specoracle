def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    result = dict(defaults)
    for seg_name in user.get("segments", []):
        if seg_name in segments:
            result.update(segments[seg_name])
    result.update(user.get("overrides", {}))
    return result
