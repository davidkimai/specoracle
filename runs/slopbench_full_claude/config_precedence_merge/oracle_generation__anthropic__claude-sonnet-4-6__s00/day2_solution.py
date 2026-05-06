"""config_precedence_merge.py

Merge settings from defaults, file config, and environment variables
with the precedence: defaults < file_config < env vars.
"""

import copy

# Keys whose values are replaced with "<redacted>" by redact_secrets.
_SENSITIVE_KEYS = {"password", "token", "secret", "api_key"}


def _parse_value(raw: str):
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


def _set_nested(target: dict, keys: list, value):
    """Write value into target at the nested path described by keys."""
    if not keys:
        raise ValueError("Keys list must not be empty.")
    for key in keys[:-1]:
        if key not in target or not isinstance(target[key], dict):
            target[key] = {}
        target = target[key]
    target[keys[-1]] = value


def _deep_merge(base: dict, override: dict) -> dict:
    """Return a new dict that is base deep-merged with override (non-mutating)."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _env_to_nested(env: dict) -> dict:
    """Extract APP__* environment variables and build a nested dict."""
    PREFIX = "APP__"
    result = {}
    for raw_key, raw_value in env.items():
        if not raw_key.startswith(PREFIX):
            continue
        remainder = raw_key[len(PREFIX):]
        if not remainder:
            raise ValueError(f"Environment variable '{raw_key}' has no key after the prefix.")
        segments = [seg.lower() for seg in remainder.split("__")]
        if any(seg == "" for seg in segments):
            raise ValueError(
                f"Environment variable '{raw_key}' produces an empty key segment."
            )
        _set_nested(result, segments, _parse_value(raw_value))
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    """
    Return a merged settings dict with precedence: defaults < file_config < env.

    Parameters
    ----------
    defaults:    Base configuration dictionary.
    file_config: File-sourced configuration; overrides defaults.
    env:         Environment variable mapping; APP__-prefixed keys override all.

    Returns
    -------
    A new dict; inputs are never mutated.
    """
    if not isinstance(defaults, dict):
        raise TypeError(f"defaults must be a dict, got {type(defaults).__name__}.")
    if not isinstance(file_config, dict):
        raise TypeError(f"file_config must be a dict, got {type(file_config).__name__}.")
    if not isinstance(env, dict):
        raise TypeError(f"env must be a dict, got {type(env).__name__}.")

    merged = _deep_merge(defaults, file_config)
    env_overrides = _env_to_nested(env)
    return _deep_merge(merged, env_overrides)


def redact_secrets(config: dict) -> dict:
    """
    Return a deep copy of *config* where any key named 'password', 'token',
    'secret', or 'api_key' (at any nesting level) has its value replaced with
    the string '<redacted>'.

    Parameters
    ----------
    config: The configuration dictionary to redact.

    Returns
    -------
    A new dict; the input is never mutated.
    """
    if not isinstance(config, dict):
        raise TypeError(f"config must be a dict, got {type(config).__name__}.")

    result = {}
    for key, value in config.items():
        if key in _SENSITIVE_KEYS:
            result[key] = "<redacted>"
        elif isinstance(value, dict):
            result[key] = redact_secrets(value)
        else:
            result[key] = copy.deepcopy(value)
    return result
