"""
config_precedence_merge
-----------------------
Merge settings from three sources with increasing precedence:
  defaults < file_config < environment variables (APP__* prefix).
"""

from __future__ import annotations

import copy
from typing import Any


# ---------------------------------------------------------------------------
# Value parsing
# ---------------------------------------------------------------------------

def _parse_value(raw: str) -> Any:
    """Parse a raw string into bool, int, list, or str."""
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
    """Return a new dict that is *override* deep-merged onto *base*.

    Both inputs are left unmodified.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


# ---------------------------------------------------------------------------
# Environment variable extraction
# ---------------------------------------------------------------------------

_ENV_PREFIX = "APP__"


def _env_key_to_path(env_key: str) -> list[str]:
    """Strip the APP__ prefix and split on '__', lowercasing each segment."""
    remainder = env_key[len(_ENV_PREFIX):]
    return [segment.lower() for segment in remainder.split("__")]


def _set_nested(mapping: dict, path: list[str], value: Any) -> None:
    """Write *value* into *mapping* at the nested location described by *path*.

    Intermediate dictionaries are created as needed.  Raises ValueError if an
    intermediate key already exists but holds a non-dict value.
    """
    if not path:
        raise ValueError("Path must have at least one segment.")

    node = mapping
    for segment in path[:-1]:
        existing = node.get(segment)
        if existing is None:
            node[segment] = {}
        elif not isinstance(existing, dict):
            raise ValueError(
                f"Cannot nest under '{segment}': existing value is not a dict."
            )
        node = node[segment]

    node[path[-1]] = value


def _parse_env(env: dict[str, str]) -> dict:
    """Return a nested dict built from APP__* environment variables."""
    result: dict = {}
    for key, raw_value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue
        path = _env_key_to_path(key)
        if not all(path):
            raise ValueError(f"Environment variable '{key}' produces an empty path segment.")
        value = _parse_value(raw_value)
        _set_nested(result, path, value)
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """Merge three configuration sources and return a new nested dict.

    Precedence (highest last, so it wins):
      defaults < file_config < environment variables

    Parameters
    ----------
    defaults:    Base configuration dictionary.
    file_config: Values from a configuration file; overrides defaults.
    env:         Mapping of environment variable names to raw string values.
                 Only keys beginning with ``APP__`` are considered.

    Returns
    -------
    dict
        A new dictionary; none of the inputs are mutated.
    """
    if not isinstance(defaults, dict):
        raise TypeError(f"defaults must be a dict, got {type(defaults).__name__!r}.")
    if not isinstance(file_config, dict):
        raise TypeError(f"file_config must be a dict, got {type(file_config).__name__!r}.")
    if not isinstance(env, dict):
        raise TypeError(f"env must be a dict, got {type(env).__name__!r}.")

    after_file = _deep_merge(defaults, file_config)
    env_overrides = _parse_env(env)
    return _deep_merge(after_file, env_overrides)
