from collections.abc import Mapping


def _require_mapping(value: object, name: str) -> Mapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    return value


def _validate_flag_map(value: object, name: str) -> Mapping[str, bool]:
    flag_map = _require_mapping(value, name)

    for key, flag_value in flag_map.items():
        if not isinstance(key, str):
            raise TypeError(f"{name} keys must be strings")
        if not isinstance(flag_value, bool):
            raise TypeError(f"{name}[{key!r}] must be a bool")

    return flag_map


def _validate_segments(segments: object) -> Mapping[str, Mapping[str, bool]]:
    segment_map = _require_mapping(segments, "segments")

    for segment_name, overrides in segment_map.items():
        if not isinstance(segment_name, str):
            raise TypeError("segments keys must be strings")
        _validate_flag_map(overrides, f"segments[{segment_name!r}]")

    return segment_map


def _user_segment_names(user: Mapping) -> list[str]:
    if "segments" not in user:
        return []

    segment_names = user["segments"]
    if not isinstance(segment_names, list):
        raise TypeError('user["segments"] must be a list of segment names')

    for index, segment_name in enumerate(segment_names):
        if not isinstance(segment_name, str):
            raise TypeError(f'user["segments"][{index}] must be a string')

    return list(segment_names)


def _user_overrides(user: Mapping) -> Mapping[str, bool]:
    if "overrides" not in user:
        return {}

    return _validate_flag_map(user["overrides"], 'user["overrides"]')


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    default_flags = _validate_flag_map(defaults, "defaults")
    segment_overrides = _validate_segments(segments)
    user_data = _require_mapping(user, "user")

    resolved = dict(default_flags)

    for segment_name in _user_segment_names(user_data):
        overrides = segment_overrides.get(segment_name)
        if overrides is not None:
            resolved.update(overrides)

    resolved.update(_user_overrides(user_data))
    return resolved
