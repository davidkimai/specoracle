def _require_dict(name: str, value: object) -> dict:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")
    return value


def _validate_flag_map(name: str, flags: object) -> dict[str, bool]:
    flag_map = _require_dict(name, flags)

    for flag_name, enabled in flag_map.items():
        if not isinstance(flag_name, str):
            raise TypeError(f"{name} keys must be strings")
        if not isinstance(enabled, bool):
            raise TypeError(f"{name}[{flag_name!r}] must be a bool")

    return flag_map


def _validate_segments(segments: object) -> dict[str, dict[str, bool]]:
    segment_map = _require_dict("segments", segments)

    for segment_name, overrides in segment_map.items():
        if not isinstance(segment_name, str):
            raise TypeError("segments keys must be strings")
        _validate_flag_map(f"segments[{segment_name!r}]", overrides)

    return segment_map


def _user_segment_names(user: dict) -> list[str]:
    if "segments" not in user:
        return []

    segment_names = user["segments"]
    if not isinstance(segment_names, list):
        raise TypeError("user['segments'] must be a list")

    for index, segment_name in enumerate(segment_names):
        if not isinstance(segment_name, str):
            raise TypeError(f"user['segments'][{index}] must be a string")

    return segment_names


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    default_flags = _validate_flag_map("defaults", defaults)
    segment_overrides = _validate_segments(segments)
    user_data = _require_dict("user", user)
    segment_names = _user_segment_names(user_data)

    if "overrides" in user_data:
        user_overrides = _validate_flag_map("user['overrides']", user_data["overrides"])
    else:
        user_overrides = {}

    resolved = dict(default_flags)

    for segment_name in segment_names:
        overrides = segment_overrides.get(segment_name)
        if overrides is not None:
            resolved.update(overrides)

    resolved.update(user_overrides)
    return resolved
