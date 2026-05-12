"""
config_precedence_merge – merge settings from defaults, file config, and
environment variables with explicit precedence: defaults < file_config < env.
"""

from __future__ import annotations

import copy
from typing import Any


# ---------------------------------------------------------------------------
# Value parsing
# ---------------------------------------------------------------------------

def _parse_value(raw: str) -> Any:
    """Parse a raw environment-variable string into a typed Python value."""
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    try:
        return int(raw, 10)
    except ValueError:
        pass
    if "," in raw:
        return [item.strip() for item in raw.split(",") if item.strip()]
    return raw


# ---------------------------------------------------------------------------
# Deep merge
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    """
    Return a new dict that is *base* deep-merged with *override*.
    Where both values are dicts, recurse.  Otherwise *override* wins.
    Neither input is mutated.
    """
    result = copy.deepcopy(base)
    for key, override_value in override.items():
        base_value = result.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, dict):
            result[key] = _deep_merge(base_value, override_value)
        else:
            result[key] = copy.deepcopy(override_value)
    return result


# ---------------------------------------------------------------------------
# Environment variable extraction
# ---------------------------------------------------------------------------

_ENV_PREFIX = "APP__"


def _env_key_to_path(env_key: str) -> list[str]:
    """
    Strip the APP__ prefix, split on __, and lowercase each segment.

    >>> _env_key_to_path("APP__DATABASE__HOST")
    ['database', 'host']
    """
    without_prefix = env_key[len(_ENV_PREFIX):]
    if not without_prefix:
        raise ValueError(f"Environment key {env_key!r} has no content after prefix.")
    segments = without_prefix.split("__")
    return [segment.lower() for segment in segments]


def _set_nested(target: dict, path: list[str], value: Any) -> None:
    """
    Write *value* into *target* at the nested location described by *path*.
    Creates intermediate dicts as needed.  Raises ValueError if an
    intermediate node exists but is not a dict.
    """
    if not path:
        raise ValueError("Path must have at least one segment.")
    node = target
    for segment in path[:-1]:
        existing = node.get(segment)
        if existing is None:
            node[segment] = {}
            node = node[segment]
        elif isinstance(existing, dict):
            node = existing
        else:
            raise ValueError(
                f"Cannot set nested key: segment {segment!r} already holds a "
                f"non-dict value ({existing!r})."
            )
    node[path[-1]] = value


def _build_env_overrides(env: dict[str, str]) -> dict:
    """
    Extract all APP__* variables from *env*, parse their values, and return
    a single nested dict representing those overrides.
    """
    overrides: dict = {}
    for key, raw_value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue
        path = _env_key_to_path(key)
        value = _parse_value(raw_value)
        _set_nested(overrides, path, value)
    return overrides


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def merge_settings(
    defaults: dict,
    file_config: dict,
    env: dict[str, str],
) -> dict:
    """
    Return a new nested settings dict merged with precedence:
        defaults < file_config < environment variables.

    Parameters
    ----------
    defaults:    Base settings dictionary.
    file_config: Settings loaded from a configuration file.
    env:         Mapping of environment variable names to their raw string
                 values (typically os.environ or a subset thereof).

    Returns
    -------
    A new dictionary; the inputs are never mutated.
    """
    if not isinstance(defaults, dict):
        raise TypeError(f"defaults must be a dict, got {type(defaults).__name__!r}.")
    if not isinstance(file_config, dict):
        raise TypeError(f"file_config must be a dict, got {type(file_config).__name__!r}.")
    if not isinstance(env, dict):
        raise TypeError(f"env must be a dict, got {type(env).__name__!r}.")

    after_file = _deep_merge(defaults, file_config)
    env_overrides = _build_env_overrides(env)
    return _deep_merge(after_file, env_overrides)
