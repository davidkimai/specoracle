from __future__ import annotations

from copy import deepcopy
import re
from typing import Any


_APP_PREFIX = "APP__"
_INT_PATTERN = re.compile(r"^[+-]?\d+$")


def _deep_merge(base: dict[Any, Any], override: dict[Any, Any]) -> dict[Any, Any]:
    result = deepcopy(base)

    for key, value in override.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def _parse_env_value(value: str) -> Any:
    lowered = value.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False

    if _INT_PATTERN.fullmatch(value):
        return int(value, 10)

    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]

    return value


def _set_nested(settings: dict[Any, Any], path: list[str], value: Any) -> None:
    current = settings

    for segment in path[:-1]:
        next_value = current.get(segment)
        if not isinstance(next_value, dict):
            next_value = {}
            current[segment] = next_value
        current = next_value

    current[path[-1]] = value


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    settings = _deep_merge(defaults, file_config)

    for key, raw_value in env.items():
        if not key.startswith(_APP_PREFIX):
            continue

        remaining_key = key[len(_APP_PREFIX):]
        path = [segment.lower() for segment in remaining_key.split("__")]
        parsed_value = _parse_env_value(raw_value)
        _set_nested(settings, path, parsed_value)

    return settings
