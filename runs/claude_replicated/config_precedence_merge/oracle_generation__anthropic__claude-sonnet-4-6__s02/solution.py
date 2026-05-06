"""
config_precedence_merge.py

Merge settings from three sources with clear precedence:
    defaults < file_config < environment variables (APP__ prefix).
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
        parts = [s.strip() for s in raw.split(",")]
        return [p for p in parts if p]
    return raw


# ---------------------------------------------------------------------------
# Nested assignment
# ---------------------------------------------------------------------------

def _set_nested(target: dict, keys: list[str], value: Any) -> None:
    """Write *value* into *target* at the location described by *keys*."""
    if not keys:
        raise ValueError("Key path must not be empty.")
    node = target
    for key in keys[:-1]:
        if key not in node:
            node[key] = {}
        elif not isinstance(node[key], dict):
            node[key] = {}
        node = node[key]
    node[keys[-1]] = value


# ---------------------------------------------------------------------------
# Deep merge
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    """Return a new dict that is *base* deep-merged with *override*.

    Neither input is mutated.  When both sides have a dict at the same key,
    the dicts are merged recursively.  Otherwise *override* wins.
    """
    result = copy.deepcopy(base)
    for key, override_val in override.items():
        base_val = result.get(key)
        if isinstance(base_val, dict) and isinstance(override_val, dict):
            result[key] = _deep_merge(base_val, override_val)
        else:
            result[key] = copy.deepcopy(override_val)
    return result


# ---------------------------------------------------------------------------
# Environment variable extraction
# ---------------------------------------------------------------------------

_PREFIX = "APP__"


def _env_to_nested(env: dict[str, str]) -> dict:
    """Build a nested dict from APP__-prefixed environment variables."""
    result: dict = {}
    for raw_key, raw_val in env.items():
        if not raw_key.startswith(_PREFIX):
            continue
        remainder = raw_key[len(_PREFIX):]
        if not remainder:
            continue
        key_path = [segment.lower() for segment in remainder.split("__")]
        if any(segment == "" for segment in key_path):
            raise ValueError(
                f"Environment variable '{raw_key}' contains an empty key segment."
            )
        value = _parse_value(raw_val)
        _set_nested(result, key_path, value)
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """Return a new nested settings dict merged with the precedence:

        defaults < file_config < environment variables.

    Parameters
    ----------
    defaults:    Base settings dictionary.
    file_config: Settings loaded from a configuration file.
    env:         Mapping of environment variable names to their string values.

    Returns
    -------
    dict
        A freshly constructed dict; none of the inputs are mutated.
    """
    if not isinstance(defaults, dict):
        raise TypeError(f"'defaults' must be a dict, got {type(defaults).__name__}.")
    if not isinstance(file_config, dict):
        raise TypeError(f"'file_config' must be a dict, got {type(file_config).__name__}.")
    if not isinstance(env, dict):
        raise TypeError(f"'env' must be a dict, got {type(env).__name__}.")

    after_file = _deep_merge(defaults, file_config)
    env_overrides = _env_to_nested(env)
    return _deep_merge(after_file, env_overrides)
