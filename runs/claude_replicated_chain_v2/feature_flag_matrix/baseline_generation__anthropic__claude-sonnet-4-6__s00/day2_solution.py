def resolve_flags(defaults: dict, segments: dict, user: dict) -> dict:
    result = dict(defaults)
    for segment_name in user.get("segments", []):
        if segment_name in segments:
            result.update(segments[segment_name])
    if "overrides" in user:
        result.update(user["overrides"])
    return result


def explain_flags(defaults: dict, segments: dict, user: dict) -> dict:
    explanation = {flag: {"value": value, "source": "default"} for flag, value in defaults.items()}

    for segment_name in user.get("segments", []):
        if segment_name in segments:
            for flag, value in segments[segment_name].items():
                explanation[flag] = {"value": value, "source": f"segment:{segment_name}"}

    if "overrides" in user:
        for flag, value in user["overrides"].items():
            explanation[flag] = {"value": value, "source": "user_override"}

    return explanation
