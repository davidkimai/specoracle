from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from typing import Any

_APP_PREFIX = "APP__"
_INTEGER_RE = re.compile(r"^[+-]?\d+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """
    Merge settings using precedence: defaults < file_config < APP__ environment variables.

    Environment variable keys beginning with APP__ are converted into nested dictionary
    paths by removing APP__, splitting on "__", and lowercasing each path segment.
    """
    merged = _deep_merge(defaults, file_config)

    for key, value in env.items():
        if not key.startswith(_APP_PREFIX):
            continue

        remainder = key[len(_APP_PREFIX) :]
        path = [segment.lower() for segment in remainder.split("__")]
        if not path:
            continue

        _set_nested(merged, path, _parse_env_value(value))

    return merged


def _deep_merge(base: Mapping[Any, Any], override: Mapping[Any, Any]) -> dict:
    result = _deep_copy_mapping(base)

    for key, override_value in override.items():
        existing_value = result.get(key)
        if isinstance(existing_value, Mapping) and isinstance(override_value, Mapping):
            result[key] = _deep_merge(existing_value, override_value)
        else:
            result[key] = _deep_copy_value(override_value)

    return result


def _deep_copy_mapping(value: Mapping[Any, Any]) -> dict:
    return {key: _deep_copy_value(item) for key, item in value.items()}


def _deep_copy_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _deep_copy_mapping(value)
    return copy.deepcopy(value)


def _parse_env_value(value: str) -> Any:
    lowered = value.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False

    if _INTEGER_RE.fullmatch(value):
        return int(value, 10)

    if "," in value:
        return [item.strip() for item in value.split(",") if item.strip()]

    return value


def _set_nested(settings: dict, path: list[str], value: Any) -> None:
    current = settings

    for segment in path[:-1]:
        next_value = current.get(segment)
        if not isinstance(next_value, dict):
            next_value = {}
            current[segment] = next_value
        current = next_value

    current[path[-1]] = value
