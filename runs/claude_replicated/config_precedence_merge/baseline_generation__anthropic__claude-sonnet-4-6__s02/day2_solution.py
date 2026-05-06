"""
config_precedence_merge.py

Implements merge_settings(defaults, file_config, env) -> dict
with precedence: defaults < file_config < environment variables.

Also implements redact_secrets(config: dict) -> dict which returns a deep copy
where keys named password, token, secret, or api_key are replaced with
"<redacted>" at any nesting level.
"""

import copy


# Keys whose values should be redacted
_SENSITIVE_KEYS = {"password", "token", "secret", "api_key"}


def _parse_value(value: str):
    """Parse a string value into bool, int, list, or str."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value, 10)
    except (ValueError, TypeError):
        pass
    if "," in value:
        parts = [p.strip() for p in value.split(",")]
        parts = [p for p in parts if p]
        return parts
    return value


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


def _env_to_nested(env: dict) -> dict:
    """
    Convert APP__-prefixed environment variables into a nested dict.
    Keys are split on '__', lowercased per segment.
    Values are parsed via _parse_value.
    """
    nested = {}
    prefix = "APP__"
    for raw_key, raw_value in env.items():
        if not raw_key.startswith(prefix):
            continue
        remainder = raw_key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__")]
        parsed = _parse_value(raw_value)
        # Build nested structure
        current = nested
        for seg in segments[:-1]:
            if seg not in current or not isinstance(current[seg], dict):
                current[seg] = {}
            current = current[seg]
        last = segments[-1]
        current[last] = parsed
    return nested


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    """
    Merge settings with precedence: defaults < file_config < environment variables.

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
    # Start from defaults
    result = copy.deepcopy(defaults)

    # Apply file_config on top
    result = _deep_merge(result, file_config)

    # Apply environment variable overrides
    env_nested = _env_to_nested(env)
    result = _deep_merge(result, env_nested)

    return result


def redact_secrets(config: dict) -> dict:
    """
    Return a deep copy of config where any key named password, token, secret,
    or api_key (at any nesting level) has its value replaced with "<redacted>".

    Parameters
    ----------
    config : dict
        The settings dictionary to redact.

    Returns
    -------
    dict
        A new dictionary with sensitive values replaced. Input is never mutated.
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
