"""
config_precedence_merge
=======================
Merge settings from defaults, a file-based config, and environment variables
with the precedence: defaults < file_config < environment variables.
"""

from __future__ import annotations

import copy
from typing import Any


# ---------------------------------------------------------------------------
# Value parsing helpers
# ---------------------------------------------------------------------------

def _parse_bool(raw: str) -> tuple[bool, Any]:
    """Return (True, bool_value) if raw is a boolean literal, else (False, None)."""
    lowered = raw.lower()
    if lowered == "true":
        return True, True
    if lowered == "false":
        return True, False
    return False, None


def _parse_int(raw: str) -> tuple[bool, Any]:
    """Return (True, int_value) if raw is a base-10 integer, else (False, None)."""
    try:
        return True, int(raw, 10)
    except ValueError:
        return False, None


def _parse_list(raw: str) -> tuple[bool, Any]:
    """Return (True, list_value) if raw contains a comma, else (False, None)."""
    if "," not in raw:
        return False, None
    return True, [item.strip() for item in raw.split(",") if item.strip()]


def _parse_value(raw: str) -> Any:
    """Parse a raw string into bool, int, list, or str."""
    matched, value = _parse_bool(raw)
    if matched:
        return value
    matched, value = _parse_int(raw)
    if matched:
        return value
    matched, value = _parse_list(raw)
    if matched:
        return value
    return raw


# ---------------------------------------------------------------------------
# Deep merge
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    """Return a new dict that is *override* merged on top of *base*.

    Both inputs are treated as read-only.  Nested dicts are merged
    recursively; all other values from *override* win outright.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


# ---------------------------------------------------------------------------
# Environment variable processing
# ---------------------------------------------------------------------------

_ENV_PREFIX = "APP__"


def _env_key_to_path(env_key: str) -> list[str]:
    """Convert an env key like APP__DATABASE__HOST to ['database', 'host']."""
    without_prefix = env_key[len(_ENV_PREFIX):]
    if not without_prefix:
        raise ValueError(f"Environment key {env_key!r} has no segments after the prefix.")
    return [segment.lower() for segment in without_prefix.split("__")]


def _set_nested(target: dict, path: list[str], value: Any) -> None:
    """Write *value* into *target* at the nested location described by *path*.

    Intermediate dicts are created as needed.  Raises ValueError when an
    intermediate key already holds a non-dict value.
    """
    for segment in path[:-1]:
        existing = target.get(segment)
        if existing is None:
            target[segment] = {}
        elif not isinstance(existing, dict):
            raise ValueError(
                f"Cannot set nested key {path!r}: "
                f"intermediate key {segment!r} holds a non-dict value {existing!r}."
            )
        target = target[segment]
    target[path[-1]] = value


def _env_to_nested(env: dict[str, str]) -> dict:
    """Convert all APP__* environment variables into a nested dict."""
    result: dict = {}
    for key, raw_value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue
        path = _env_key_to_path(key)
        value = _parse_value(raw_value)
        _set_nested(result, path, value)
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """Return a merged settings dict with precedence: defaults < file_config < env.

    Parameters
    ----------
    defaults:    Base settings dictionary.
    file_config: Settings loaded from a configuration file.
    env:         Mapping of environment variable names to their string values.

    Returns
    -------
    A new dictionary; none of the inputs are mutated.
    """
    after_file = _deep_merge(defaults, file_config)
    env_overrides = _env_to_nested(env)
    return _deep_merge(after_file, env_overrides)
