"""
config_precedence_merge
=======================
Merge layered configuration with the precedence:
    defaults < file_config < environment variables (APP__*)
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
    """Return a new dict that is *override* deep-merged onto *base*."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


# ---------------------------------------------------------------------------
# Environment variable expansion
# ---------------------------------------------------------------------------

_ENV_PREFIX = "APP__"


def _env_to_nested(env: dict[str, str]) -> dict:
    """
    Convert APP__-prefixed env vars into a nested dict.

    APP__DATABASE__HOST=localhost  ->  {"database": {"host": "localhost"}}
    """
    result: dict = {}
    for key, raw_value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue
        remainder = key[len(_ENV_PREFIX):]
        if not remainder:
            raise ValueError(f"Environment variable {key!r} has no key after the prefix.")
        segments = [seg.lower() for seg in remainder.split("__")]
        if any(seg == "" for seg in segments):
            raise ValueError(
                f"Environment variable {key!r} contains an empty segment after splitting on '__'."
            )
        value = _parse_value(raw_value)
        _set_nested(result, segments, value)
    return result


def _set_nested(mapping: dict, keys: list[str], value: Any) -> None:
    """Write *value* into *mapping* at the path described by *keys* (in-place)."""
    for key in keys[:-1]:
        if key not in mapping:
            mapping[key] = {}
        elif not isinstance(mapping[key], dict):
            # A scalar was set at a higher level; replace it with a dict.
            mapping[key] = {}
        mapping = mapping[key]
    mapping[keys[-1]] = value


# ---------------------------------------------------------------------------
# Secret redaction
# ---------------------------------------------------------------------------

_REDACTED_KEYS = {"password", "token", "secret", "api_key"}
_REDACTED_PLACEHOLDER = "<redacted>"


def redact_secrets(config: dict) -> dict:
    """
    Return a deep copy of *config* where any key named 'password', 'token',
    'secret', or 'api_key' (at any nesting level) has its value replaced with
    '<redacted>'.  The input is never mutated.
    """
    if not isinstance(config, dict):
        raise TypeError(f"config must be a dict, got {type(config).__name__!r}")
    return _redact_dict(config)


def _redact_dict(mapping: dict) -> dict:
    result = {}
    for key, value in mapping.items():
        if key in _REDACTED_KEYS:
            result[key] = _REDACTED_PLACEHOLDER
        elif isinstance(value, dict):
            result[key] = _redact_dict(value)
        else:
            result[key] = copy.deepcopy(value)
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def merge_settings(
    defaults: dict,
    file_config: dict,
    env: dict[str, str],
) -> dict:
    """
    Return a merged settings dict with precedence: defaults < file_config < env.

    Parameters
    ----------
    defaults:    Base configuration values.
    file_config: Values loaded from a config file; override defaults.
    env:         Environment variable mapping; APP__-prefixed keys override all.

    Returns
    -------
    A new dict; none of the inputs are mutated.
    """
    if not isinstance(defaults, dict):
        raise TypeError(f"defaults must be a dict, got {type(defaults).__name__!r}")
    if not isinstance(file_config, dict):
        raise TypeError(f"file_config must be a dict, got {type(file_config).__name__!r}")
    if not isinstance(env, dict):
        raise TypeError(f"env must be a dict, got {type(env).__name__!r}")

    merged = _deep_merge(defaults, file_config)
    env_layer = _env_to_nested(env)
    merged = _deep_merge(merged, env_layer)
    return merged
