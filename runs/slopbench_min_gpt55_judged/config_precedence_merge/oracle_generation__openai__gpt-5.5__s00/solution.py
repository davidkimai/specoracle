from __future__ import annotations

from copy import deepcopy
import re
from typing import Any


_INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")
_ENV_PREFIX = "APP__"


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    _require_dict("defaults", defaults)
    _require_dict("file_config", file_config)
    _require_dict("env", env)

    merged = _deep_merge(defaults, file_config)
    env_config = _environment_config(env)
    return _deep_merge(merged, env_config)


def _require_dict(name: str, value: object) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _deep_merge(base: dict, override: dict) -> dict:
    result = deepcopy(base)

    for key, override_value in override.items():
        base_value = result.get(key)

        if isinstance(base_value, dict) and isinstance(override_value, dict):
            result[key] = _deep_merge(base_value, override_value)
            continue

        result[key] = deepcopy(override_value)

    return result


def _environment_config(env: dict[str, str]) -> dict:
    config: dict[str, Any] = {}

    for name, value in env.items():
        if not isinstance(name, str):
            raise TypeError("environment variable names must be strings")
        if not isinstance(value, str):
            raise TypeError(f"environment variable {name!r} must have a string value")
        if not name.startswith(_ENV_PREFIX):
            continue

        path = _environment_path(name)
        parsed_value = _parse_value(value)
        _set_nested_value(config, path, parsed_value, name)

    return config


def _environment_path(name: str) -> list[str]:
    remainder = name[len(_ENV_PREFIX) :]
    segments = remainder.split("__")

    if not remainder or any(segment == "" for segment in segments):
        raise ValueError(f"environment variable {name!r} has an invalid settings path")

    return [segment.lower() for segment in segments]


def _parse_value(value: str) -> Any:
    lowered = value.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INTEGER_PATTERN.fullmatch(value):
        return int(value, 10)
    if "," in value:
        return [item.strip() for item in value.split(",") if item.strip()]

    return value


def _set_nested_value(
    config: dict[str, Any],
    path: list[str],
    value: Any,
    source_name: str,
) -> None:
    current = config

    for segment in path[:-1]:
        existing = current.get(segment)

        if existing is None:
            next_config: dict[str, Any] = {}
            current[segment] = next_config
            current = next_config
            continue

        if not isinstance(existing, dict):
            raise ValueError(
                f"environment variable {source_name!r} conflicts with another "
                f"environment variable at {segment!r}"
            )

        current = existing

    leaf = path[-1]
    existing_leaf = current.get(leaf)

    if isinstance(existing_leaf, dict):
        raise ValueError(
            f"environment variable {source_name!r} conflicts with another "
            f"environment variable at {leaf!r}"
        )

    current[leaf] = value
