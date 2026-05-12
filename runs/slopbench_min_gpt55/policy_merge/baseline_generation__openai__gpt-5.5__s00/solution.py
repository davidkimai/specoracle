from copy import deepcopy
from typing import Any


def merge_policy(defaults: dict, override: dict) -> dict:
    """
    Merge two policy dictionaries without mutating either input.

    Rules:
    - Values from override take precedence over values from defaults.
    - If both corresponding values are dictionaries, they are merged recursively.
    - If override contains a key with value None, that key is removed from the result.
    """
    if not isinstance(defaults, dict):
        raise TypeError("defaults must be a dict")
    if not isinstance(override, dict):
        raise TypeError("override must be a dict")

    result = deepcopy(defaults)

    for key, override_value in override.items():
        if override_value is None:
            result.pop(key, None)
            continue

        default_value = result.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = merge_policy(default_value, override_value)
        else:
            result[key] = deepcopy(override_value)

    return result
