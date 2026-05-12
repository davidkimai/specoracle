from __future__ import annotations

import copy
import re
from typing import Any, Mapping

_ENV_PREFIX = "APP__"
_INT_RE = re.compile(r"^[+-]?\d+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    merged = _deep_merge(defaults, file_config)

    for key, value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue

        path = [segment.lower() for segment in key[len(_ENV_PREFIX) :].split("__")]
        _set_nested(merged, path, _parse_env_value(value))

    return merged


def _deep_merge(base: Mapping[Any, Any], override: Mapping[Any, Any]) -> dict:
    result = copy.deepcopy(dict(base))

    for key, value in override.items():
        if isinstance(result.get(key), dict) and isinstance(value, Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def _set_nested(settings: dict, path: list[str], value: Any) -> None:
    current = settings

    for segment in path[:-1]:
        existing = current.get(segment)
        if not isinstance(existing, dict):
            existing = {}
            current[segment] = existing
        current = existing

    current[path[-1]] = value


def _parse_env_value(value: str) -> Any:
    stripped = value.strip()
    lowered = stripped.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INT_RE.fullmatch(stripped):
        return int(stripped, 10)
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]

    return value
