from __future__ import annotations

from copy import deepcopy
from typing import Any


def merge_policy(defaults: dict, override: dict) -> dict:
    """Merge policy dictionaries without mutating either input."""
    _require_dict(defaults, "defaults")
    _require_dict(override, "override")
    return _merge_dicts(defaults, override)


def _require_dict(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _merge_dicts(defaults: dict, override: dict) -> dict:
    result = {key: _copy_value(value) for key, value in defaults.items()}

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        default_value = result.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = _merge_dicts(default_value, override_value)
            continue

        result[key] = _copy_override_value(override_value)

    return result


def _copy_override_value(value: Any) -> Any:
    if isinstance(value, dict):
        return _merge_dicts({}, value)
    return deepcopy(value)


def _copy_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _copy_value(child) for key, child in value.items()}
    return deepcopy(value)
