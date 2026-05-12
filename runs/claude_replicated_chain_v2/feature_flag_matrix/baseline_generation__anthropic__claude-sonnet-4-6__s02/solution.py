def resolve_flags(defaults: dict[str, bool], segments: dict[str, dict[str, bool]], user: dict) -> dict[str, bool]:
    result = dict(defaults)

    for segment_name in user.get("segments", []):
        if segment_name in segments:
            result.update(segments[segment_name])

    if "overrides" in user:
        result.update(user["overrides"])

    return result
