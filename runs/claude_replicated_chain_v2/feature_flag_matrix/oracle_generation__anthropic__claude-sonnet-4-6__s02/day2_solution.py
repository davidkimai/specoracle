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


def explain_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, dict]:
    explained: dict[str, dict] = {}

    for flag, value in defaults.items():
        explained[flag] = {"value": value, "source": "default"}

    for segment_name in user.get("segments", []):
        if segment_name in segments:
            for flag, value in segments[segment_name].items():
                explained[flag] = {"value": value, "source": f"segment:{segment_name}"}

    if "overrides" in user:
        for flag, value in user["overrides"].items():
            explained[flag] = {"value": value, "source": "user_override"}

    return explained
