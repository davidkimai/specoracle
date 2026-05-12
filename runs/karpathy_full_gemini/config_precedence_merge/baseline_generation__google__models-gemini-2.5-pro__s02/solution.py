# -*- coding: utf-8 -*-
"""
A module for merging configuration settings from multiple sources with a
defined precedence order.
"""

import copy
from typing import Any, Dict, List, Union

__all__ = ["merge_settings"]


def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deeply merges the source dictionary into a deep copy of the target.

    Does not mutate the input dictionaries. If a key exists in both and both
    values are dictionaries, they are merged recursively. Otherwise, the value
    from the source dictionary overwrites the value in the target.

    Args:
        target: The base dictionary.
        source: The dictionary to merge into the target.

    Returns:
        A new dictionary with the merged content.
    """
    result = copy.deepcopy(target)
    for key, value in source.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _parse_value(value: str) -> Union[bool, int, List[str], str]:
    """
    Parses a string value into a typed Python object.

    - "true"/"false" (case-insensitive) become booleans.
    - Base-10 integer strings become ints.
    - Comma-separated strings become lists of trimmed, non-empty strings.
    - Other strings are returned as is.

    Args:
        value: The string value to parse.

    Returns:
        The parsed value.
    """
    sanitized_value = value.strip()

    # Boolean check
    if sanitized_value.lower() == "true":
        return True
    if sanitized_value.lower() == "false":
        return False

    # Integer check (base-10)
    if sanitized_value.isdigit() or (
        sanitized_value.startswith("-") and sanitized_value[1:].isdigit()
    ):
        try:
            return int(sanitized_value)
        except ValueError:
            # This path should not be reached due to the preceding checks
            pass

    # Comma-separated list check
    if "," in sanitized_value:
        return [item.strip() for item in sanitized_value.split(",") if item.strip()]

    # Default to returning the original string (not the stripped one)
    return value


def _parse_env_vars(env: Dict[str, str]) -> Dict[str, Any]:
    """
    Parses environment variables into a nested dictionary configuration.

    Considers only variables starting with "APP__", splits them by "__" to
    create a nested structure, and parses their values.

    Args:
        env: A dictionary of environment variables.

    Returns:
        A nested dictionary representing the configuration from the environment.
    """
    config: Dict[str, Any] = {}
    prefix = "APP__"

    for key, value in env.items():
        if not key.startswith(prefix):
            continue

        path_str = key[len(prefix) :]
        if not path_str:
            continue

        path = [part.lower() for part in path_str.split("__") if part]
        if not path:
            continue

        parsed_value = _parse_value(value)

        current_level = config
        for part in path[:-1]:
            # If a non-dictionary value is at a path segment, it will be
            # overwritten to allow for a more specific nested setting.
            if not isinstance(current_level.get(part), dict):
                current_level[part] = {}
            current_level = current_level[part]

        current_level[path[-1]] = parsed_value

    return config


def merge_settings(
    defaults: Dict[str, Any],
    file_config: Dict[str, Any],
    env: Dict[str, str],
) -> Dict[str, Any]:
    """
    Merges settings from multiple sources with a defined precedence order.

    The precedence is: defaults < file_config < environment variables.
    The merge is deep for dictionaries. Input dictionaries are not mutated.

    Environment variables are parsed as follows:
    - Only keys starting with "APP__" are considered.
    - The "APP__" prefix is removed, and the rest of the key is split by "__".
    - Each segment of the key is lowercased to form a path in a nested dict.
    - Values are parsed: "true"/"false" become booleans, integer strings
      become ints, and comma-separated strings become lists of strings.

    Args:
        defaults: A dictionary of default settings.
        file_config: A dictionary of settings loaded from a configuration file.
        env: A dictionary of environment variables (e.g., os.environ).

    Returns:
        A new dictionary containing the final, merged settings.
    """
    # 1. Merge defaults and file_config. _deep_merge returns a new dict.
    merged_settings = _deep_merge(defaults, file_config)

    # 2. Parse environment variables into a dictionary structure.
    env_settings = _parse_env_vars(env)

    # 3. Merge environment variable settings on top of the previous result.
    final_settings = _deep_merge(merged_settings, env_settings)

    return final_settings
