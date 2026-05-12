from __future__ import annotations

from typing import Any

FlagMap = dict[str, bool]
SegmentMap = dict[str, FlagMap]


def _require_dict(value: object, name: str) -> dict[Any, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dictionary")
    return value


def _validate_flag_map(value: object, name: str) -> FlagMap:
    mapping = _require_dict(value, name)

    for flag_name, enabled in mapping.items():
        if not isinstance(flag_name, str):
            raise TypeError(f"{name} keys must be strings")
        if not isinstance(enabled, bool):
            raise TypeError(f"{name}[{flag_name!r}] must be a boolean")

    return mapping


def _validate_segments(value: object) -> SegmentMap:
    mapping = _require_dict(value, "segments")

    for segment_name, overrides in mapping.items():
        if not isinstance(segment_name, str):
            raise TypeError("segments keys must be strings")
        _validate_flag_map(overrides, f"segments[{segment_name!r}]")

    return mapping


def _user_segment_names(user: dict[Any, Any]) -> list[str]:
    if "segments" not in user:
        return []

    names = user["segments"]
    if not isinstance(names, list):
        raise TypeError('user["segments"] must be a list')

    for index, name in enumerate(names):
        if not isinstance(name, str):
            raise TypeError(f'user["segments"][{index}] must be a string')

    return list(names)


def _user_overrides(user: dict[Any, Any]) -> FlagMap:
    if "overrides" not in user:
        return {}

    return _validate_flag_map(user["overrides"], 'user["overrides"]')


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    validated_defaults = _validate_flag_map(defaults, "defaults")
    validated_segments = _validate_segments(segments)
    validated_user = _require_dict(user, "user")

    segment_names = _user_segment_names(validated_user)
    user_overrides = _user_overrides(validated_user)

    resolved = dict(validated_defaults)

    for segment_name in segment_names:
        if segment_name in validated_segments:
            resolved.update(validated_segments[segment_name])

    resolved.update(user_overrides)
    return resolved
