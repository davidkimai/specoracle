from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from typing import Any

APP_ENV_PREFIX = "APP__"
_INTEGER_RE = re.compile(r"^[+-]?\d+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    _require_mapping(defaults, "defaults")
    _require_mapping(file_config, "file_config")
    _require_mapping(env, "env")

    merged_config = _deep_merge_mappings(defaults, file_config)
    env_config = _settings_from_environment(env)
    return _deep_merge_mappings(merged_config, env_config)


def _require_mapping(value: Any, name: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")


def _deep_merge_mappings(base: Mapping[Any, Any], overlay: Mapping[Any, Any]) -> dict:
    result = _copy_mapping(base)

    for key, overlay_value in overlay.items():
        existing_value = result.get(key)

        if key in result and _is_mapping(existing_value) and _is_mapping(overlay_value):
            result[key] = _deep_merge_mappings(existing_value, overlay_value)
            continue

        result[key] = _copy_value(overlay_value)

    return result


def _copy_mapping(source: Mapping[Any, Any]) -> dict:
    return {key: _copy_value(value) for key, value in source.items()}


def _copy_value(value: Any) -> Any:
    if _is_mapping(value):
        return _copy_mapping(value)

    return copy.deepcopy(value)


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _settings_from_environment(env: Mapping[Any, Any]) -> dict:
    settings: dict = {}

    for key, value in env.items():
        if not isinstance(key, str):
            raise TypeError("env keys must be strings")
        if not isinstance(value, str):
            raise TypeError(f"env value for {key!r} must be a string")
        if not key.startswith(APP_ENV_PREFIX):
            continue

        path = _environment_path(key)
        parsed_value = _parse_environment_value(value)
        _write_environment_value(settings, path, parsed_value, key)

    return settings


def _environment_path(key: str) -> list[str]:
    path_text = key[len(APP_ENV_PREFIX) :]

    if not path_text:
        raise ValueError(f"environment variable {key!r} does not contain a setting path")

    segments = path_text.split("__")

    if any(segment == "" for segment in segments):
        raise ValueError(f"environment variable {key!r} contains an empty path segment")

    return [segment.lower() for segment in segments]


def _parse_environment_value(value: str) -> Any:
    if value == "true":
        return True
    if value == "false":
        return False
    if _INTEGER_RE.fullmatch(value):
        return int(value, 10)
    if "," in value:
        return [item for item in (part.strip() for part in value.split(",")) if item]

    return value


def _write_environment_value(root: dict, path: list[str], value: Any, source_key: str) -> None:
    current = root

    for segment in path[:-1]:
        if segment not in current:
            current[segment] = {}

        next_value = current[segment]
        if not isinstance(next_value, dict):
            raise ValueError(
                f"environment variable {source_key!r} conflicts with an existing scalar setting"
            )

        current = next_value

    leaf = path[-1]
    existing_value = current.get(leaf)

    if isinstance(existing_value, dict):
        raise ValueError(
            f"environment variable {source_key!r} conflicts with an existing nested setting"
        )

    current[leaf] = value
