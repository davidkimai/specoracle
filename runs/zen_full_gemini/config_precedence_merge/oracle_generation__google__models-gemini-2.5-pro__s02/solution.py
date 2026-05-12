"""
Merges configuration settings from multiple sources with defined precedence.
"""

import copy
from typing import Any


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> None:
    """
    Recursively merges the 'overrides' dictionary into the 'base' dictionary.

    If a key exists in both dictionaries and both values are dictionaries,
    it merges them recursively. Otherwise, the value from 'overrides'
    replaces the value in 'base'.

    This function modifies the 'base' dictionary in-place.

    Args:
        base: The dictionary to merge into.
        overrides: The dictionary with values to merge from.
    """
    for key, value in overrides.items():
        if key in base and isinstance(base.get(key), dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _parse_env_key(env_key: str) -> list[str]:
    """
    Parses an environment variable key into a list of nested dictionary keys.

    Expects format 'APP__KEY1__KEY2' and returns ['key1', 'key2'].

    Args:
        env_key: The environment variable key string.

    Returns:
        A list of strings representing the path for the nested setting.

    Raises:
        ValueError: If the key format is invalid (e.g., empty segments).
    """
    prefix = "APP__"
    # This function assumes the key starts with the prefix, as checked by its caller.
    key_part = env_key[len(prefix) :]
    if not key_part:
        raise ValueError("Invalid env key: key is empty after prefix.")

    segments = key_part.split("__")
    if any(not s for s in segments):
        raise ValueError(f"Invalid env key: contains empty segments in '{env_key}'.")

    return [s.lower() for s in segments]


def _parse_env_value(value_str: str) -> Any:
    """
    Parses a string value from an environment variable into a Python type.
