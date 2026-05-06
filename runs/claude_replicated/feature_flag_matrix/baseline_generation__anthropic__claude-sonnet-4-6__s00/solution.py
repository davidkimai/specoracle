def resolve_flags(defaults: dict, segments: dict, user: dict) -> dict:
    result = dict(defaults)
    for segment_name in user.get("segments", []):
        if segment_name in segments:
            result.update(segments[segment_name])
    if "overrides" in user:
        result.update(user["overrides"])
    return result
