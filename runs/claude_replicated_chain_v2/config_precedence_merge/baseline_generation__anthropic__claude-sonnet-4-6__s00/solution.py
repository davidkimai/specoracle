"""
config_precedence_merge.py

Implements merge_settings(defaults, file_config, env) -> dict

Precedence: defaults < file_config < environment variables (APP__ prefix).
"""

import copy


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
        parts = [p.strip() for p in value.split(",") if p.strip()]
        return parts
    return value


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge two dictionaries. Values in override take precedence.
    Dictionaries are merged recursively; other types are replaced.
    Neither input is mutated.
    """
    result = copy.deepcopy(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result


def _set_nested(d: dict, keys: list, value):
    """
    Set a value in a nested dict structure given a list of keys.
    Intermediate dicts are created as needed.
    """
    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value


def _env_to_dict(env: dict) -> dict:
    """
    Parse environment variables with APP__ prefix into a nested dict.
    """
    result = {}
    prefix = "APP__"
    for key, value in env.items():
        if not key.startswith(prefix):
            continue
        remainder = key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__") if seg]
        if not segments:
            continue
        parsed = _parse_value(value)
        _set_nested(result, segments, parsed)
    return result


def merge_settings(defaults: dict, file_config: dict, env: dict) -> dict:
    """
    Merge settings with precedence: defaults < file_config < env vars.

    Args:
        defaults: Base default settings dictionary.
        file_config: Settings loaded from a configuration file.
        env: Environment variables (dict[str, str]).

    Returns:
        A new merged settings dictionary. Input dicts are never mutated.
    """
    # Start with defaults
    result = copy.deepcopy(defaults)

    # Apply file_config on top
    result = _deep_merge(result, file_config)

    # Parse and apply environment variables on top
    env_dict = _env_to_dict(env)
    result = _deep_merge(result, env_dict)

    return result
