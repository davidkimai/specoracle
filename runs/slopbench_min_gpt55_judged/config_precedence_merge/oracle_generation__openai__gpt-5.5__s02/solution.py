from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import re


_ENV_PREFIX = "APP__"
_INTEGER_PATTERN = re.compile(r"[+-]?\d+")


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    _require_dict("defaults", defaults)
    _require_dict("file_config", file_config)
    _require_dict("env", env)

    merged = _deep_merge(defaults, file_config)
    env_config = _parse_environment(env)
    return _deep_merge(merged, env_config)


def _require_dict(name: str, value: object) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")


def _deep_merge(base: Mapping, override: Mapping) -> dict:
    result = {key: deepcopy(value) for key, value in base.items()}

    for key, override_value in override.items():
        base_value = result.get(key)

        if isinstance(base_value, Mapping) and isinstance(override_value, Mapping):
            result[key] = _deep_merge(base_value, override_value)
            continue

        result[key] = deepcopy(override_value)

    return result


def _parse_environment(env: dict[str, str]) -> dict:
    parsed: dict = {}

    for key, value in env.items():
        _require_env_item(key, value)

        if not key.startswith(_ENV_PREFIX):
            continue

        path = _env_key_to_path(key)
        parsed_value = _parse_env_value(value)
        _set_nested_value(parsed, path, parsed_value)

    return parsed


def _require_env_item(key: object, value: object) -> None:
    if not isinstance(key, str):
        raise TypeError("env keys must be strings")
    if not isinstance(value, str):
        raise TypeError(f"env value for {key!r} must be a string")


def _env_key_to_path(key: str) -> list[str]:
    remainder = key[len(_ENV_PREFIX) :]

    if not remainder:
        raise ValueError(f"environment key {key!r} has no setting path")

    path = [segment.lower() for segment in remainder.split("__")]

    if any(segment == "" for segment in path):
        raise ValueError(f"environment key {key!r} contains an empty path segment")

    return path


def _parse_env_value(value: str) -> object:
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


def _set_nested_value(settings: dict, path: list[str], value: object) -> None:
    current = settings

    for segment in path[:-1]:
        existing = current.get(segment)

        if existing is None:
            child: dict = {}
            current[segment] = child
            current = child
            continue

        if not isinstance(existing, dict):
            full_path = "__".join(path)
            raise ValueError(f"environment setting {full_path!r} conflicts with another setting")

        current = existing

    leaf = path[-1]

    if leaf in current:
        full_path = "__".join(path)
        raise ValueError(f"environment setting {full_path!r} is defined more than once")

    current[leaf] = value
