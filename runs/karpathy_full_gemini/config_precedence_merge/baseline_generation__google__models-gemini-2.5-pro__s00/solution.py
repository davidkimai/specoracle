# -*- coding: utf-8 -*-
"""
A module for merging configuration settings from multiple sources.
"""

import copy
from typing import Any, Dict, List, Union

__all__ = ["merge_settings"]


def _parse_env_value(value: str) -> Union[bool, int, List[str], str]:
    """
    Parses a string value from an environment variable into a Python type.

    - "true"/"false" (case-insensitive) are parsed as booleans.
    - Base-10 integers are parsed as ints.
    - Comma-separated strings are parsed as lists of non-empty, trimmed strings.
    - Other values are returned as strings.
    """
    # Boolean parsing (case-insensitive)
    val_lower = value.lower()
    if val_lower == 'true':
        return True
    if val_lower == 'false':
        return False

    # Integer parsing
    try:
        return int(value, 10)
    except ValueError:
        pass

    # List parsing for comma-separated values
    if ',' in value:
        return [s.strip() for s in value.split(',') if s.strip()]

    # Default to returning the original string
    return value


def _parse_env_config(env: Dict[str, str]) -> Dict[str, Any]:
    """
    Constructs a nested dictionary from environment variables.

    Only variables starting with 'APP__' are considered. The prefix is
    stripped, and the rest of the key is split by '__' to create the
    nested structure. Each segment is lowercased.
    """
    config: Dict[str, Any] = {}
    prefix = 'APP__'
    prefix_len = len(prefix)

    for key, value in env.items():
        if not key.startswith(prefix):
            continue

        key_path_str = key[prefix_len:]
        if not key_path_str:
            continue

        key_path = [part.lower() for part in key_path_str.split('__')]
        parsed_value = _parse_env_value(value)

        current_level = config
        # Navigate through the path, creating dicts as needed
        for part in key_path[:-1]:
            # If a non-dict value exists at this path, it will be replaced
            # by a dict to allow for further nesting.
            if not isinstance(current_level.get(part), dict):
                current_level[part] = {}
            current_level = current_level[part]

        # Set the final value
        current_level[key_path[-1]] = parsed_value

    return config


def _deep_merge(base: Dict[str, Any], overrides: Dict[str, Any]) -> None:
    """
    Recursively merges the 'overrides' dictionary into the 'base' dictionary.

    This function mutates the 'base' dictionary.
    """
    for key, value in overrides.items():
        if isinstance(base.get(key), dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def merge_settings(
    defaults: dict, file_config: dict, env: Dict[str, str]
) -> dict:
    """
    Merges settings from multiple sources with a defined precedence.

    The precedence order is: defaults < file_config < environment variables.
    Higher precedence sources override lower ones. Dictionaries are merged
    deeply.

    Environment variables are parsed as follows:
    - Must start with the prefix 'APP__'.
    - The key is split by '__' to determine the nested path. Segments are
      lowercased.
    - Values are parsed into bools, ints, lists of strings, or strings.

    Args:
        defaults: A dictionary of default settings.
        file_config: A dictionary of settings from a configuration file.
        env: A dictionary of environment variables (e.g., os.environ).

    Returns:
        A new nested dictionary containing the merged settings. The input
        dictionaries are not mutated.
    """
    # Start with a deep copy of defaults to ensure inputs are not mutated.
    settings = copy.deepcopy(defaults)

    # Merge settings from file_config.
    _deep_merge(settings, file_config)

    # Parse environment variables and merge them with the highest precedence.
    env_config = _parse_env_config(env)
    _deep_merge(settings, env_config)

    return settings
