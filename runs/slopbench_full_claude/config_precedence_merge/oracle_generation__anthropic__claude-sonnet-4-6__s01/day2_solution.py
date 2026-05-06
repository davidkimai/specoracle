"""config_precedence_merge.py

Merge settings from three sources with explicit precedence:
    defaults < file_config < environment variables (APP__* keys).
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
    """Return a new dict that deep-merges *override* on top of *base*.

    Both inputs are left unmodified.  When both sides hold a dict at the same
    key, the merge recurses.  Otherwise *override* wins.
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

def _env_key_to_path(env_key: str) -> list[str]:
    """Convert 'APP__a__b__c' to ['a', 'b', 'c'] (lowercase segments)."""
    without_prefix = env_key[len("APP__"):]
    return [segment.lower() for segment in without_prefix.split("__")]


def _set_nested(mapping: dict, path: list[str], value: Any) -> None:
    """Write *value* into *mapping* at the nested location described by *path*.

    Intermediate dicts are created as needed.  Raises ValueError when an
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


def _env_to_nested(env: dict[str, str]) -> dict:
    """Build a nested dict from APP__* environment variables."""
    result: dict = {}
    for key, raw_value in env.items():
        if not key.startswith("APP__"):
            continue
        path = _env_key_to_path(key)
        if not path or any(segment == "" for segment in path):
            raise ValueError(f"Invalid environment variable key: '{key}'.")
        parsed = _parse_value(raw_value)
        _set_nested(result, path, parsed)
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def merge_settings(
    defaults: dict,
    file_config: dict,
    env: dict[str, str],
) -> dict:
    """Return a merged settings dict with precedence: defaults < file_config < env.

    Args:
        defaults:    Base configuration dictionary.
        file_config: File-sourced configuration; overrides *defaults*.
        env:         Environment variable mapping; APP__* keys override both.

    Returns:
        A new dictionary.  The three input dicts are never mutated.
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


# ---------------------------------------------------------------------------
# Secret redaction
# ---------------------------------------------------------------------------

_SENSITIVE_KEYS = frozenset({"password", "token", "secret", "api_key"})


def redact_secrets(config: dict) -> dict:
    """Return a deep copy of *config* with sensitive values replaced.

    Keys named ``password``, ``token``, ``secret``, or ``api_key`` (at any
    nesting level) have their values replaced with the string ``"<redacted>"``.
    All other values are deep-copied unchanged.  The input dict is never
    mutated.

    Args:
        config: The settings dictionary to redact.

    Returns:
        A new dictionary with sensitive keys redacted.
    """
    if not isinstance(config, dict):
        raise TypeError(f"'config' must be a dict, got {type(config).__name__}.")

    result: dict = {}
    for key, value in config.items():
        if key in _SENSITIVE_KEYS:
            result[key] = "<redacted>"
        elif isinstance(value, dict):
            result[key] = redact_secrets(value)
        else:
            result[key] = copy.deepcopy(value)
    return result
