from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from typing import Any

APP_PREFIX = "APP__"
_INTEGER_PATTERN = re.compile(r"[+-]?\d+")
_MISSING = object()


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """Merge defaults, file configuration, and APP__ environment settings."""
    _require_mapping(defaults, "defaults")
    _require_mapping(file_config, "file_config")
    _require_mapping(env, "env")

    merged = _deep_merge(defaults, file_config)
    env_settings = _settings_from_environment(env)
    return _deep_merge(merged, env_settings)


def _require_mapping(value: Any, name: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a dictionary")


def _deep_merge(base: Mapping, override: Mapping) -> dict:
    merged = copy.deepcopy(dict(base))

    for key, override_value in override.items():
        base_value = merged.get(key, _MISSING)

        if isinstance(base_value, dict) and isinstance(override_value, dict):
            merged[key] = _deep_merge(base_value, override_value)
            continue

        merged[key] = copy.deepcopy(override_value)

    return merged


def _settings_from_environment(env: Mapping) -> dict:
    settings: dict[str, Any] = {}

    for key, value in env.items():
        if not isinstance(key, str):
            raise TypeError("env keys must be strings")
        if not isinstance(value, str):
            raise TypeError(f"env value for {key!r} must be a string")
        if not key.startswith(APP_PREFIX):
            continue

        path = _environment_path(key)
        parsed_value = _parse_environment_value(value)
        _set_nested_value(settings, path, parsed_value, key)

    return settings


def _environment_path(key: str) -> tuple[str, ...]:
    remainder = key[len(APP_PREFIX) :]
    segments = remainder.split("__")

    if not remainder or any(segment == "" for segment in segments):
        raise ValueError(f"environment key {key!r} contains an empty path segment")

    return tuple(segment.lower() for segment in segments)


def _parse_environment_value(value: str) -> Any:
    if value == "true":
        return True
    if value == "false":
        return False
    if _INTEGER_PATTERN.fullmatch(value):
        return int(value, 10)
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]
    return value


def _set_nested_value(
    settings: dict[str, Any],
    path: tuple[str, ...],
    value: Any,
    source_key: str,
) -> None:
    current = settings

    for segment in path[:-1]:
        existing = current.get(segment, _MISSING)

        if existing is _MISSING:
            next_level: dict[str, Any] = {}
            current[segment] = next_level
            current = next_level
            continue

        if not isinstance(existing, dict):
            dotted_path = ".".join(path)
            raise ValueError(
                f"environment key {source_key!r} conflicts while setting {dotted_path!r}"
            )

        current = existing

    leaf = path[-1]
    if leaf in current:
        dotted_path = ".".join(path)
        raise ValueError(
            f"multiple environment keys set the same setting {dotted_path!r}"
        )

    current[leaf] = value
