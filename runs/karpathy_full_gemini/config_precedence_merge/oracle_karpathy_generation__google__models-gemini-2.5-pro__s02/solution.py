import copy
from typing import Any, Dict, List, Union


def _deep_merge_dicts(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges two dictionaries, creating a new dictionary.
    """
    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if key in merged and isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = _deep_merge_dicts(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _parse_env_var_value(value: str) -> Union[bool, int, List[str], str]:
    """
    Parses a string value from an environment variable into a Python type.
    """
    val_lower = value.lower()
    if val_lower == "true":
        return True
    if val_lower == "false":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    if "," in value:
        return [item.strip() for item in value.split(",") if item.strip()]

    return value


def merge_settings(
    defaults: Dict[str, Any],
    file_config: Dict[str, Any],
    env: Dict[str, str],
) -> Dict[str, Any]:
    """
    Merges settings from defaults, a file, and environment variables.

    The precedence order is: defaults < file_config < environment variables.
    The merge is deep for dictionaries. Input dictionaries are not mutated.

    Environment variables must be prefixed with 'APP__'. The prefix is stripped,
    the rest of the key is split by '__', and each part is lowercased to form
    a nested key path.

    Values from environment variables are parsed as follows:
    - 'true'/'false' (case-insensitive) become booleans.
    - Base-10 integers become ints.
    - Comma-separated strings become lists of non-empty, trimmed strings.
    - Other values remain strings.

    Args:
        defaults: A dictionary of default settings.
        file_config: A dictionary of settings from a configuration file.
        env: A dictionary representing the environment variables.

    Returns:
        A new nested dictionary containing the final merged settings.
    """
    settings = _deep_merge_dicts(defaults, file_config)

    env_prefix = "APP__"
    for key, value in env.items():
        if not key.startswith(env_prefix):
            continue

        path_str = key[len(env_prefix) :]
        if not path_str:
            continue

        path_segments = [segment.lower() for segment in path_str.split("__")]
        parsed_value = _parse_env_var_value(value)

        current_level = settings
        for segment in path_segments[:-1]:
            if not isinstance(current_level.get(segment), dict):
                current_level[segment] = {}
            current_level = current_level[segment]

        last_segment = path_segments[-1]
        current_level[last_segment] = parsed_value

    return settings
