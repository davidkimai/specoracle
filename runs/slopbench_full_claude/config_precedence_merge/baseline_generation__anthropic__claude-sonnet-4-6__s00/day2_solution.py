"""
config_precedence_merge.py

Implements merge_settings(defaults, file_config, env) -> dict
with precedence: defaults < file_config < environment variables.

Also implements redact_secrets(config) -> dict which replaces sensitive
key values with "<redacted>" at any nesting level.
"""

import copy
from typing import Any


def _parse_value(raw: str) -> Any:
    """Parse a raw string value into bool, int, list, or str."""
    stripped = raw.strip()

    # Boolean
    if stripped.lower() == "true":
        return True
    if stripped.lower() == "false":
        return False

    # Integer (base-10)
    try:
        return int(stripped, 10)
    except ValueError:
        pass

    # Comma-separated list (only if comma is present)
    if "," in stripped:
        parts = [p.strip() for p in stripped.split(",")]
        parts = [p for p in parts if p]  # remove empty strings
        return parts

    # Plain string
    return stripped


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge override into base, returning a new dict.
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
    Set a nested value in dict d using the list of keys.
    Intermediate dicts are created as needed.
    Mutates d in place (caller should pass a scratch dict).
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
    result: dict = {}
    prefix = "APP__"
    for raw_key, raw_value in env.items():
        if not raw_key.startswith(prefix):
            continue
        remainder = raw_key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__")]
        # Filter out empty segments
        segments = [s for s in segments if s]
        if not segments:
            continue
        parsed = _parse_value(raw_value)
        _set_nested(result, segments, parsed)
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    """
    Merge settings with precedence: defaults < file_config < env.

    Parameters
    ----------
    defaults : dict
        Base default settings.
    file_config : dict
        Settings loaded from a configuration file.
    env : dict[str, str]
        Environment variables mapping. Keys beginning with APP__ are parsed
        into nested settings.

    Returns
    -------
    dict
        A new nested settings dictionary. Input dicts are never mutated.
    """
    # Start with defaults
    result = copy.deepcopy(defaults)

    # Apply file_config over defaults
    result = _deep_merge(result, file_config)

    # Parse and apply environment variables
    env_config = _parse_env(env)
    result = _deep_merge(result, env_config)

    return result


_SENSITIVE_KEYS = {"password", "token", "secret", "api_key"}


def redact_secrets(config: dict) -> dict:
    """
    Return a deep copy of config where any key named 'password', 'token',
    'secret', or 'api_key' has its value replaced with '<redacted>',
    at any nesting level. The input dict is never mutated.

    Parameters
    ----------
    config : dict
        The settings dictionary to redact.

    Returns
    -------
    dict
        A new dictionary with sensitive values replaced.
    """
    result = {}
    for key, value in config.items():
        if key in _SENSITIVE_KEYS:
            result[key] = "<redacted>"
        elif isinstance(value, dict):
            result[key] = redact_secrets(value)
        else:
            result[key] = copy.deepcopy(value)
    return result
