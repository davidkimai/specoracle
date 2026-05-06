"""
config_precedence_merge.py

Implements merge_settings(defaults, file_config, env) -> dict
with precedence: defaults < file_config < environment variables (APP__...).
"""

import copy
from typing import Any


def _parse_value(raw: str) -> Any:
    """Parse a string value into bool, int, list, or str."""
    stripped = raw.strip()

    # Boolean
    if stripped.lower() == "true":
        return True
    if stripped.lower() == "false":
        return False

    # Integer (base-10 only)
    try:
        # Avoid treating floats as ints
        parsed = int(stripped, 10)
        # Make sure the string is actually an integer representation
        # (int() would succeed for "0x1f" with base 0, but we use base 10)
        return parsed
    except ValueError:
        pass

    # Comma-separated list: only treat as list if there's a comma present
    if "," in stripped:
        parts = [p.strip() for p in stripped.split(",")]
        parts = [p for p in parts if p]  # remove empty strings
        return parts

    # Default: string
    return stripped


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge override into base. Returns a new dict.
    Neither base nor override is mutated.
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
    Mutates d in place (caller must ensure d is a fresh copy).
    """
    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value


def _parse_env(env: dict) -> dict:
    """
    Parse environment variables starting with APP__ into a nested dict.
    """
    result = {}
    prefix = "APP__"
    for raw_key, raw_value in env.items():
        if not raw_key.startswith(prefix):
            continue
        remainder = raw_key[len(prefix):]
        if not remainder:
            continue
        segments = [seg.lower() for seg in remainder.split("__") if seg]
        if not segments:
            continue
        parsed = _parse_value(raw_value)
        _set_nested(result, segments, parsed)
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    """
    Merge settings with precedence: defaults < file_config < env vars.

    Parameters
    ----------
    defaults : dict
        Default settings (lowest precedence).
    file_config : dict
        File-based configuration.
    env : dict[str, str]
        Environment variables. Keys starting with APP__ are parsed and merged
        with the highest precedence.

    Returns
    -------
    dict
        A new merged settings dictionary. Inputs are never mutated.
    """
    # Start with defaults
    merged = copy.deepcopy(defaults)

    # Apply file_config on top
    merged = _deep_merge(merged, file_config)

    # Parse and apply environment variables on top
    env_config = _parse_env(env)
    merged = _deep_merge(merged, env_config)

    return merged
