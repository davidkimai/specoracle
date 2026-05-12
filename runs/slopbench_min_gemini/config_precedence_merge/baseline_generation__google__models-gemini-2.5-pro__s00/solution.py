import copy
from typing import Any, Dict, List, Union

# Environment variable prefix for application-specific settings.
_ENV_PREFIX = "APP__"
# Delimiter used for nesting keys in environment variables.
_ENV_DELIMITER = "__"


def _parse_env_value(value: str) -> Union[bool, int, List[str], str]:
    """
    Parses a string value from an environment variable into a Python type.

    - "true"/"false" (case-insensitive) are parsed as booleans.
    - Base-10 integers are parsed as ints.
    - Comma-separated strings are parsed as lists of non-empty, trimmed strings.
    - Other values remain strings.
    """
    cleaned_value = value.strip()
    
    # Boolean parsing
    if cleaned_value.lower() == "true":
        return True
    if cleaned_value.lower() == "false":
        return False

    # Integer parsing
    if cleaned_value.isdecimal():
        return int(cleaned_value)
    
    # List parsing for comma-separated values
    if "," in cleaned_value:
        return [item.strip() for item in cleaned_value.split(",") if item.strip()]

    # Default to string
    return value


def _parse_env(env: Dict[str, str]) -> Dict[str, Any]:
    """
    Parses environment variables into a nested dictionary.

    Only variables starting with "APP__" are considered. The key is split
    by "__", lowercased, and used to create a nested structure.
    """
    config: Dict[str, Any] = {}
    for key, value in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue

        path_str = key[len(_ENV_PREFIX):]
        if not path_str:
            continue

        path_keys = [p.lower() for p in path_str.split(_ENV_DELIMITER)]
        parsed_value = _parse_env_value(value)

        current_level = config
        # Traverse or create the nested dictionary structure
        for part in path_keys[:-1]:
            if part not in current_level:
                current_level[part] = {}
            # If a non-dictionary value exists, it cannot be traversed
            if not isinstance(current_level[part], dict):
                # In this case, we skip setting the value to avoid overwriting
                # a scalar with a dictionary fragment, which is ambiguous.
                # A more opinionated implementation might raise an error.
                break
            current_level = current_level[part]
        else:
             # Set the value at the final key
             current_level[path_keys[-1]] = parsed_value
            
    return config


def _deep_merge(source: Dict[str, Any], destination: Dict[str, Any]) -> None:
    """
    Recursively merges a source dictionary into a destination dictionary.

    Modifies the destination dictionary in place.
    """
    for key, value in source.items():
        if isinstance(value, dict) and key in destination and isinstance(destination[key], dict):
            _deep_merge(value, destination[key])
        else:
            destination[key] = value


def merge_settings(defaults: dict, file_config: dict, env: Dict[str, str]) -> dict:
    """
    Merges settings from three sources with a defined precedence.

    The precedence order is: defaults < file_config < environment variables.
    Higher precedence sources override lower ones. Dictionaries are merged
    deeply.

    Args:
        defaults: A dictionary of default settings.
        file_config: A dictionary of settings loaded from a configuration file.
        env: A dictionary representing environment variables (e.g., from os.environ).

    Returns:
        A new dictionary containing the merged settings.
    """
    # Start with a deep copy of defaults to ensure immutability of inputs
    merged_settings = copy.deepcopy(defaults)

    # Merge file_config into the defaults
    _deep_merge(file_config, merged_settings)

    # Parse environment variables and merge them with the highest precedence
    env_config = _parse_env(env)
    _deep_merge(env_config, merged_settings)

    return merged_settings
