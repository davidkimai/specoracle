from __future__ import annotations

import copy
import re
from typing import Any

_ENV_PREFIX = "APP__"
_INTEGER_RE = re.compile(r"^[+-]?[0-9]+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """
    Merge settings with precedence:
        defaults < file_config < APP__ environment variables

    Environment variable names are parsed by removing the APP__ prefix, splitting
    the remainder on "__", and lowercasing each path segment.
    """
    merged = _deep_merge_dicts(defaults, file_config)

    for key, value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue

        path = [segment.lower() for segment in key[len(_ENV_PREFIX) :].split("__")]
        _set_nested_value(merged, path, _parse_env_value(value))

    return merged


def _deep_merge_dicts(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)

    for key, override_value in override.items():
        base_value = result.get(key)

        if isinstance(base_value, dict) and isinstance(override_value, dict):
            result[key] = _deep_merge_dicts(base_value, override_value)
        else:
            result[key] = copy.deepcopy(override_value)

    return result


def _set_nested_value(settings: dict, path: list[str], value: Any) -> None:
    current = settings

    for segment in path[:-1]:
        next_value = current.get(segment)
        if not isinstance(next_value, dict):
            next_value = {}
            current[segment] = next_value
        current = next_value

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
