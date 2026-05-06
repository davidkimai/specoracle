def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    result = dict(defaults)

    for segment_name in user.get("segments", []):
        if segment_name in segments:
            result.update(segments[segment_name])

    if "overrides" in user:
        result.update(user["overrides"])

    return result


def explain_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, dict]:
    # Track value and source for each flag
    result: dict[str, dict] = {}

    # Start from defaults
    for flag, value in defaults.items():
        result[flag] = {"value": value, "source": "default"}

    # Apply segment overrides in order
    for segment_name in user.get("segments", []):
        if segment_name in segments:
            for flag, value in segments[segment_name].items():
                result[flag] = {"value": value, "source": f"segment:{segment_name}"}

    # Apply user overrides
    for flag, value in user.get("overrides", {}).items():
        result[flag] = {"value": value, "source": "user_override"}

    return result
