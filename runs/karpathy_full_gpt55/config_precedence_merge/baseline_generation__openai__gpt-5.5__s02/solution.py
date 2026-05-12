from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from typing import Any


_ENV_PREFIX = "APP__"
_INTEGER_RE = re.compile(r"^[+-]?\d+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """
    Merge settings using precedence:
        defaults < file_config < APP__ environment variables

    Environment variable names are converted to nested paths by removing the
    APP__ prefix, splitting on "__", and lowercasing each segment.
    """
    merged = _deep_merge(defaults, file_config)

    for key, value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue

        remainder = key[len(_ENV_PREFIX) :]
        path = [segment.lower() for segment in remainder.split("__")]
        _set_nested(merged, path, _parse_env_value(value))

    return merged


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict:
    result = copy.deepcopy(dict(base))

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], Mapping)
            and isinstance(value, Mapping)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def _set_nested(target: dict, path: list[str], value: Any) -> None:
    current = target

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
