from __future__ import annotations

from copy import deepcopy
import re
from typing import Any


_APP_PREFIX = "APP__"
_INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """Merge settings with precedence: defaults < file_config < APP__ env vars."""
    _require_dict("defaults", defaults)
    _require_dict("file_config", file_config)
    _require_dict("env", env)

    merged_config = _deep_merge(defaults, file_config)
    environment_config = _environment_config(env)
    return _deep_merge(merged_config, environment_config)


def _require_dict(name: str, value: Any) -> None:
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

    for key, value in env.items():
        _require_env_item(key, value)

        if not key.startswith(_APP_PREFIX):
            continue

        path = _environment_path(key)
        parsed_value = _parse_env_value(value)
        _set_nested_value(config, path, parsed_value, key)

    return config


def _require_env_item(key: Any, value: Any) -> None:
    if not isinstance(key, str):
        raise TypeError("env keys must be strings")

    if not isinstance(value, str):
        raise TypeError(f"env value for {key!r} must be a string")


def _environment_path(key: str) -> tuple[str, ...]:
    remainder = key[len(_APP_PREFIX) :]

    if not remainder:
        raise ValueError(f"environment variable {key!r} has no setting path")

    segments = remainder.split("__")

    if any(segment == "" for segment in segments):
        raise ValueError(f"environment variable {key!r} contains an empty path segment")

    return tuple(segment.lower() for segment in segments)


def _parse_env_value(value: str) -> Any:
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
    target: dict[str, Any],
    path: tuple[str, ...],
    value: Any,
    source_key: str,
) -> None:
    current = target

    for segment in path[:-1]:
        if segment not in current:
            current[segment] = {}
            current = current[segment]
            continue

        next_value = current[segment]

        if not isinstance(next_value, dict):
            joined_path = "__".join(path)
            raise ValueError(
                f"environment variable {source_key!r} conflicts at {joined_path!r}"
            )

        current = next_value

    leaf = path[-1]

    if leaf in current:
        joined_path = "__".join(path)
        raise ValueError(
            f"environment variable {source_key!r} duplicates or conflicts at {joined_path!r}"
        )

    current[leaf] = value
