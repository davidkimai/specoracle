def _require_dict(value: object, name: str) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _validate_flag_map(value: object, name: str) -> None:
    _require_dict(value, name)

    for flag_name, enabled in value.items():
        if not isinstance(flag_name, str):
            raise TypeError(f"{name} keys must be strings")
        if not isinstance(enabled, bool):
            raise TypeError(f"{name}[{flag_name!r}] must be a bool")


def _validate_segments(segments: object) -> None:
    _require_dict(segments, "segments")

    for segment_name, overrides in segments.items():
        if not isinstance(segment_name, str):
            raise TypeError("segments keys must be strings")
        _validate_flag_map(overrides, f"segments[{segment_name!r}]")


def _user_segment_names(user: dict) -> list[str]:
    if "segments" not in user:
        return []

    names = user["segments"]
    if not isinstance(names, list):
        raise TypeError('user["segments"] must be a list of strings')

    for name in names:
        if not isinstance(name, str):
            raise TypeError('user["segments"] must be a list of strings')

    return names


def _user_overrides(user: dict) -> dict[str, bool]:
    if "overrides" not in user:
        return {}

    overrides = user["overrides"]
    _validate_flag_map(overrides, 'user["overrides"]')
    return overrides


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    _validate_flag_map(defaults, "defaults")
    _validate_segments(segments)
    _require_dict(user, "user")

    resolved = dict(defaults)

    for segment_name in _user_segment_names(user):
        if segment_name in segments:
            resolved.update(segments[segment_name])

    resolved.update(_user_overrides(user))
    return resolved
