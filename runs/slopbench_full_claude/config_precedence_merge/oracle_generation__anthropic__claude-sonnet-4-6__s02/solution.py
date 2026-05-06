"""
config_precedence_merge
=======================
Merge settings from defaults, file config, and environment variables
with precedence: defaults < file_config < environment variables.
"""

from __future__ import annotations

import copy


def _parse_value(raw: str) -> bool | int | list | str:
    """Parse a raw string into a typed Python value."""
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    try:
        return int(raw, 10)
    except ValueError:
        pass
    if "," in raw:
        parts = [part.strip() for part in raw.split(",")]
        return [p for p in parts if p]
    return raw


def _env_to_nested(env: dict[str, str]) -> dict:
    """Convert APP__-prefixed env vars into a nested dict."""
    result: dict = {}
    prefix = "APP__"
    for key, raw_value in env.items():
        if not key.startswith(prefix):
            continue
        remainder = key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__")]
        if not all(segments):
            raise ValueError(
                f"Environment variable {key!r} contains empty path segment."
            )
        value = _parse_value(raw_value)
        _set_nested(result, segments, value)
    return result


def _set_nested(target: dict, segments: list[str], value) -> None:
    """Write *value* into *target* at the path described by *segments*."""
    node = target
    for seg in segments[:-1]:
        if seg not in node:
            node[seg] = {}
        elif not isinstance(node[seg], dict):
            node[seg] = {}
        node = node[seg]
    node[segments[-1]] = value


def _deep_merge(base: dict, override: dict) -> dict:
    """Return a new dict that is *override* deep-merged onto *base*."""
    merged = copy.deepcopy(base)
    for key, override_value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, dict):
            merged[key] = _deep_merge(base_value, override_value)
        else:
            merged[key] = copy.deepcopy(override_value)
    return merged


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """
    Merge settings with precedence: defaults < file_config < env vars.

    Parameters
    ----------
    defaults:    Base settings dictionary.
    file_config: Settings loaded from a config file.
    env:         Mapping of environment variable names to their string values.

    Returns
    -------
    A new nested dictionary; inputs are never mutated.
    """
    if not isinstance(defaults, dict):
        raise TypeError(f"defaults must be a dict, got {type(defaults).__name__!r}")
    if not isinstance(file_config, dict):
        raise TypeError(f"file_config must be a dict, got {type(file_config).__name__!r}")
    if not isinstance(env, dict):
        raise TypeError(f"env must be a dict, got {type(env).__name__!r}")

    env_overrides = _env_to_nested(env)

    after_file = _deep_merge(defaults, file_config)
    after_env = _deep_merge(after_file, env_overrides)
    return after_env
