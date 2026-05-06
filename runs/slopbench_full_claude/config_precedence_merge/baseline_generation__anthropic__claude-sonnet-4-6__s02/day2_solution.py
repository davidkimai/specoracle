"""
config_precedence_merge.py

Implements merge_settings(defaults, file_config, env) with precedence:
defaults < file_config < environment variables (APP__ prefix).

Also implements redact_secrets(config) which replaces sensitive keys with
"<redacted>" at any nesting level.
"""

import copy
from typing import Any


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge override into base, returning a new dict.
    Neither input is mutated.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _parse_env_value(raw: str) -> Any:
    """
    Parse a raw environment variable string into a Python value.

    - "true" / "false" (case-insensitive) -> bool
    - base-10 integer string -> int
    - comma-separated string (contains comma) -> list of non-empty trimmed strings
    - otherwise -> str
    """
    # Boolean check
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False

    # Integer check
    try:
        return int(raw, 10)
    except ValueError:
        pass

    # Comma-separated list check
    if "," in raw:
        parts = [s.strip() for s in raw.split(",")]
        return [p for p in parts if p]

    return raw


def _set_nested(target: dict, keys: list, value: Any) -> None:
    """
    Set a value in a nested dict structure given a list of keys.
    Intermediate dicts are created as needed.
    """
    for key in keys[:-1]:
        if key not in target or not isinstance(target[key], dict):
            target[key] = {}
        target = target[key]
    target[keys[-1]] = value


def _env_to_dict(env: dict) -> dict:
    """
    Convert environment variables with APP__ prefix into a nested dict.
    """
    result: dict = {}
    prefix = "APP__"
    for raw_key, raw_value in env.items():
        if not raw_key.startswith(prefix):
            continue
        remainder = raw_key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__")]
        # Filter out empty segments that could arise from double underscores
        segments = [s for s in segments if s]
        if not segments:
            continue
        parsed_value = _parse_env_value(raw_value)
        _set_nested(result, segments, parsed_value)
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    """
    Merge settings with precedence: defaults < file_config < environment variables.

    Parameters
    ----------
    defaults : dict
        Base default settings (lowest precedence).
    file_config : dict
        Settings loaded from a config file (medium precedence).
    env : dict[str, str]
        Environment variables; keys starting with APP__ are parsed and applied
        with highest precedence.

    Returns
    -------
    dict
        A new nested settings dictionary. Input dicts are never mutated.
    """
    # Start with defaults
    merged = copy.deepcopy(defaults)

    # Apply file_config on top
    merged = _deep_merge(merged, file_config)

    # Parse env vars and apply on top
    env_dict = _env_to_dict(env)
    merged = _deep_merge(merged, env_dict)

    return merged


_SENSITIVE_KEYS = {"password", "token", "secret", "api_key"}


def redact_secrets(config: dict) -> dict:
    """
    Return a deep copy of config where any key named 'password', 'token',
    'secret', or 'api_key' (at any nesting level) has its value replaced
    with "<redacted>". The input dict is never mutated.

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
