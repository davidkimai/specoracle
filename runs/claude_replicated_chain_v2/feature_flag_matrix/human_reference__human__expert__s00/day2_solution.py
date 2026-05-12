def resolve_flags(defaults: dict[str, bool], segments: dict[str, dict[str, bool]], user: dict) -> dict[str, bool]:
    resolved = dict(defaults)
    for segment_name in user.get("segments", []):
        resolved.update(segments.get(segment_name, {}))
    resolved.update(user.get("overrides", {}))
    return resolved


def explain_flags(defaults: dict[str, bool], segments: dict[str, dict[str, bool]], user: dict) -> dict[str, dict]:
    explained = {flag: {"value": value, "source": "default"} for flag, value in defaults.items()}

    for segment_name in user.get("segments", []):
        for flag, value in segments.get(segment_name, {}).items():
            explained[flag] = {"value": value, "source": f"segment:{segment_name}"}

    for flag, value in user.get("overrides", {}).items():
        explained[flag] = {"value": value, "source": "user_override"}

    return explained
