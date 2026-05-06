from __future__ import annotations

from copy import deepcopy


def merge_policy(defaults: dict, override: dict, *, allow_delete: bool = True) -> dict:
    result = deepcopy(defaults)
    for key, value in override.items():
        if value is None:
            if allow_delete:
                result.pop(key, None)
            continue

        current = result.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            result[key] = merge_policy(current, value, allow_delete=allow_delete)
            continue
        result[key] = deepcopy(value)
    return result
