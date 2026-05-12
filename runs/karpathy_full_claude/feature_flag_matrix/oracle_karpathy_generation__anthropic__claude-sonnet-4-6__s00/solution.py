def resolve_flags(defaults: dict, segments: dict, user: dict) -> dict:
    result = dict(defaults)
    for seg in user.get("segments", []):
        if seg in segments:
            result.update(segments[seg])
    result.update(user.get("overrides", {}))
    return result
