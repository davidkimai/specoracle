"""Feature flag resolution."""

from typing import Any

__all__ = ["resolve_flags"]


def resolve_flags(
    defaults: dict[str, bool],
    segments: dict[str, dict[str, bool]],
    user: dict,
) -> dict[str, bool]:
    """Resolve flags from defaults, ordered segment overrides, and user overrides."""
    base_flags = _require_flag_map(defaults, "defaults")
    segment_overrides = _require_segments(segments)
    user_data = _require_dict(user, "user")

    resolved = dict(base_flags)

    for segment_name in _user_segment_names(user_data):
        overrides = segment_overrides.get(segment_name)
        if overrides is not None:
            resolved.update(overrides)

    if "overrides" in user_data:
        resolved.update(_require_flag_map(user_data["overrides"], 'user["overrides"]'))

    return resolved


def _require_dict(value: Any, name: str) -> dict:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")
    return value


def _require_flag_map(value: Any, name: str) -> dict[str, bool]:
    flag_map = _require_dict(value, name)

    for flag_name, enabled in flag_map.items():
        if not isinstance(flag_name, str):
            raise TypeError(f"{name} keys must be str")
        if type(enabled) is not bool:
            raise TypeError(f"{name}[{flag_name!r}] must be bool")

    return flag_map


def _require_segments(value: Any) -> dict[str, dict[str, bool]]:
    segment_map = _require_dict(value, "segments")

    for segment_name, overrides in segment_map.items():
        if not isinstance(segment_name, str):
            raise TypeError("segments keys must be str")
        _require_flag_map(overrides, f"segments[{segment_name!r}]")

    return segment_map


def _user_segment_names(user: dict) -> list[str]:
    if "segments" not in user:
        return []

    segment_names = user["segments"]
    if not isinstance(segment_names, list):
        raise TypeError('user["segments"] must be a list')

    for index, segment_name in enumerate(segment_names):
        if not isinstance(segment_name, str):
            raise TypeError(f'user["segments"][{index}] must be str')

    return list(segment_names)
