from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from typing import Any

_APP_PREFIX = "APP__"
_INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """Merge defaults, file configuration, and APP__ environment overrides."""
    _require_mapping(defaults, "defaults")
    _require_mapping(file_config, "file_config")
    _require_mapping(env, "env")

    merged = _deep_merge(defaults, file_config)

    for key, value in env.items():
        if not isinstance(key, str):
            raise TypeError("env keys must be strings")
        if not isinstance(value, str):
            raise TypeError(f"env value for {key!r} must be a string")
        if not key.startswith(_APP_PREFIX):
            continue

        path = _env_path(key)
        parsed_value = _parse_env_value(value)
        _set_nested_value(merged, path, parsed_value)

    return merged


def _require_mapping(value: Any, name: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a dictionary-like mapping")


def _deep_merge(base: Mapping, override: Mapping) -> dict:
    result = _deep_copy_mapping(base)

    for key, override_value in override.items():
        if (
            key in result
            and isinstance(result[key], Mapping)
            and isinstance(override_value, Mapping)
        ):
            result[key] = _deep_merge(result[key], override_value)
            continue

        result[key] = copy.deepcopy(override_value)

    return result


def _deep_copy_mapping(source: Mapping) -> dict:
    return {key: copy.deepcopy(value) for key, value in source.items()}


def _env_path(key: str) -> list[str]:
    raw_path = key[len(_APP_PREFIX) :]
    if not raw_path:
        raise ValueError("environment override key must include a setting path")

    segments = raw_path.split("__")
    if any(segment == "" for segment in segments):
        raise ValueError(f"environment override key has an empty path segment: {key!r}")

    return [segment.lower() for segment in segments]


def _parse_env_value(value: str) -> Any:
    lowered = value.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INTEGER_PATTERN.fullmatch(value):
        return int(value, 10)
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]

    return value


def _set_nested_value(settings: dict, path: list[str], value: Any) -> None:
    current = settings

    for segment in path[:-1]:
        existing = current.get(segment)
        if existing is None:
            next_mapping: dict = {}
            current[segment] = next_mapping
            current = next_mapping
            continue

        if not isinstance(existing, dict):
            raise ValueError(
                "environment override path conflicts with a non-dictionary setting: "
                f"{'.'.join(path)!r}"
            )

        current = existing

    leaf = path[-1]
    if isinstance(current.get(leaf), dict) and not isinstance(value, dict):
        current[leaf] = value
        return

    current[leaf] = value
