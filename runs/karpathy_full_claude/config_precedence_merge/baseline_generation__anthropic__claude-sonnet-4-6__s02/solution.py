"""
config_precedence_merge.py

Implements merge_settings for layered configuration with precedence:
    defaults < file_config < environment variables (APP__ prefix)
"""

import copy
from typing import Any


def _parse_env_value(value: str) -> Any:
    """Parse a string env value into bool, int, list, or string."""
    # Check boolean
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    # Check integer (base-10)
    try:
        return int(value, 10)
    except ValueError:
        pass

    # Check comma-separated list
    if "," in value:
        parts = [part.strip() for part in value.split(",")]
        # Filter out empty strings
        parts = [p for p in parts if p]
        return parts

    # Default: string
    return value


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge override into base. Returns a new dict without mutating inputs.
    For each key in override:
      - If both base[key] and override[key] are dicts, recursively merge.
      - Otherwise, override[key] takes precedence.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _set_nested(d: dict, keys: list, value: Any) -> None:
    """
    Set a value in a nested dict given a list of keys.
    Intermediate dicts are created as needed.
    Mutates d in place (used only on a scratch dict).
    """
    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value


def _parse_env_vars(env: dict) -> dict:
    """
    Parse environment variables with APP__ prefix into a nested dict.
    Keys are split on __, lowercased per segment.
    """
    result = {}
    prefix = "APP__"
    for raw_key, raw_value in env.items():
        if not raw_key.startswith(prefix):
            continue
        # Strip prefix and split on __
        remainder = raw_key[len(prefix):]
        segments = remainder.split("__")
        # Lowercase each segment
        keys = [seg.lower() for seg in segments if seg]  # skip empty segments
        if not keys:
            continue
        parsed_value = _parse_env_value(raw_value)
        _set_nested(result, keys, parsed_value)
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    """
    Merge settings with precedence: defaults < file_config < env vars.

    Parameters
    ----------
    defaults : dict
        Base default settings.
    file_config : dict
        Settings loaded from a configuration file.
    env : dict[str, str]
        Environment variables; those starting with APP__ are parsed and applied.

    Returns
    -------
    dict
        A new merged settings dictionary. Input dicts are never mutated.
    """
    # Start with defaults
    merged = copy.deepcopy(defaults)

    # Apply file_config on top
    merged = _deep_merge(merged, file_config)

    # Parse and apply env vars
    env_settings = _parse_env_vars(env)
    merged = _deep_merge(merged, env_settings)

    return merged
