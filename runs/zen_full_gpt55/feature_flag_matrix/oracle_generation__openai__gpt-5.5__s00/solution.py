from collections.abc import Mapping
from typing import Any

__all__ = ["resolve_flags"]


def _require_mapping(name: str, value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    return value


def _copy_flag_map(name: str, value: Any) -> dict[str, bool]:
    mapping = _require_mapping(name, value)
    result: dict[str, bool] = {}

    for flag_name, enabled in mapping.items():
        if not isinstance(flag_name, str):
            raise TypeError(f"{name} keys must be strings")
        if not isinstance(enabled, bool):
            raise TypeError(f"{name}[{flag_name!r}] must be a bool")
        result[flag_name] = enabled

    return result


def _segment_names(user: Mapping[str, Any]) -> list[str]:
    if "segments" not in user:
        return []

    names = user["segments"]
    if not isinstance(names, list):
        raise TypeError("user['segments'] must be a list of strings")

    for index, name in enumerate(names):
        if not isinstance(name, str):
            raise TypeError(f"user['segments'][{index}] must be a string")

    return list(names)


def _user_overrides(user: Mapping[str, Any]) -> dict[str, bool]:
    if "overrides" not in user:
        return {}
    return _copy_flag_map("user['overrides']", user["overrides"])


def _copy_segments(value: Any) -> dict[str, dict[str, bool]]:
    mapping = _require_mapping("segments", value)
    result: dict[str, dict[str, bool]] = {}

    for segment_name, overrides in mapping.items():
        if not isinstance(segment_name, str):
            raise TypeError("segments keys must be strings")
        result[segment_name] = _copy_flag_map(f"segments[{segment_name!r}]", overrides)

    return result


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    user_mapping = _require_mapping("user", user)

    resolved = _copy_flag_map("defaults", defaults)
    known_segments = _copy_segments(segments)

    for segment_name in _segment_names(user_mapping):
        segment_overrides = known_segments.get(segment_name)
        if segment_overrides is not None:
            resolved.update(segment_overrides)

    resolved.update(_user_overrides(user_mapping))
    return resolved
