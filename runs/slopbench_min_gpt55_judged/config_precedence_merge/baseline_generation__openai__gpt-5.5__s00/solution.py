from __future__ import annotations

import copy
import re
from typing import Any


_ENV_PREFIX = "APP__"
_INTEGER_RE = re.compile(r"^[+-]?\d+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """
    Merge settings from defaults, file configuration, and environment variables.

    Precedence:
        defaults < file_config < environment variables

    Environment variables must begin with "APP__". The remainder of the key is
    split on "__", lowercased, and used as a nested path.
    """
    merged = _deep_merge(defaults, file_config)

    for key, value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue

        path = [segment.lower() for segment in key[len(_ENV_PREFIX) :].split("__")]
        _set_nested(merged, path, _parse_env_value(value))

    return merged


def _deep_merge(base: dict, override: dict) -> dict:
    result: dict[str, Any] = {}

    for key, value in base.items():
        result[key] = copy.deepcopy(value)

    for key, value in override.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def _set_nested(settings: dict, path: list[str], value: Any) -> None:
    current = settings

    for segment in path[:-1]:
        next_value = current.get(segment)
        if not isinstance(next_value, dict):
            next_value = {}
            current[segment] = next_value
        current = next_value

    if path:
        current[path[-1]] = value


def _parse_env_value(value: str) -> Any:
    lowered = value.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INTEGER_RE.fullmatch(value):
        return int(value, 10)
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]

    return value
