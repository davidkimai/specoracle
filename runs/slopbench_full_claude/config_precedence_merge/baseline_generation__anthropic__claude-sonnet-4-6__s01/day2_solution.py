"""
config_precedence_merge.py

Implements merge_settings(defaults, file_config, env) -> dict

Precedence: defaults < file_config < environment variables (APP__ prefix).

Also implements redact_secrets(config: dict) -> dict, which returns a deep copy
where keys named password, token, secret, or api_key are replaced with
"<redacted>" at any nesting level.
"""

import copy

_REDACTED_KEYS = {"password", "token", "secret", "api_key"}


def _parse_value(value: str):
    """Parse a string value into bool, int, list, or str."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value, 10)
    except ValueError:
        pass
    if "," in value:
        parts = [p.strip() for p in value.split(",")]
        parts = [p for p in parts if p]
        return parts
    return value


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge override into base. Returns a new dict without mutating inputs.
    For keys present in both, if both values are dicts, recurse.
    Otherwise override wins.
    """
    result = copy.deepcopy(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result


def _env_to_nested(env: dict) -> dict:
    """
    Parse environment variables with APP__ prefix into a nested dict.
    Key segments are split on __ and lowercased.
    """
    result = {}
    prefix = "APP__"
    for key, raw_value in env.items():
        if not key.startswith(prefix):
            continue
        remainder = key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__")]
        if not segments or any(seg == "" for seg in segments):
            continue
        parsed = _parse_value(raw_value)
        # Build nested dict from segments
        nested = parsed
        for seg in reversed(segments):
            nested = {seg: nested}
        result = _deep_merge(result, nested)
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    """
    Merge settings with precedence: defaults < file_config < env vars.

    Parameters
    ----------
    defaults : dict
        Base default settings.
    file_config : dict
        Settings loaded from a config file.
    env : dict[str, str]
        Environment variables mapping. Keys starting with APP__ are parsed.

    Returns
    -------
    dict
        A new merged settings dictionary. Input dicts are never mutated.
    """
    # Start with defaults
    merged = copy.deepcopy(defaults)
    # Apply file_config on top
    merged = _deep_merge(merged, file_config)
    # Apply env vars on top
    env_nested = _env_to_nested(env)
    merged = _deep_merge(merged, env_nested)
    return merged


def redact_secrets(config: dict) -> dict:
    """
    Return a deep copy of config where any key named 'password', 'token',
    'secret', or 'api_key' (at any nesting level) has its value replaced
    with '<redacted>'. The input dict is never mutated.

    Parameters
    ----------
    config : dict
        The configuration dictionary to redact.

    Returns
    -------
    dict
        A new dictionary with sensitive keys redacted.
    """
    result = {}
    for key, val in config.items():
        if key in _REDACTED_KEYS:
            result[key] = "<redacted>"
        elif isinstance(val, dict):
            result[key] = redact_secrets(val)
        else:
            result[key] = copy.deepcopy(val)
    return result
