from __future__ import annotations

from typing import Any


def flatten_paths(value: dict[Any, Any]) -> dict[str, object]:
    """
    Flatten a nested dictionary into a dictionary keyed by dot-separated paths.

    Nested dictionaries are expanded recursively. Lists and all other non-dict
    values are treated as leaf values.

    Examples:
        {"a": {"b": 1}, "c": [2, 3]} -> {"a.b": 1, "c": [2, 3]}

    Empty dictionaries are preserved as leaf values so that information is not
    lost during flattening.
    """
    if not isinstance(value, dict):
        raise TypeError("flatten_paths() expects a dictionary")

    flattened: dict[str, object] = {}

    def walk(mapping: dict[Any, Any], prefix: str) -> None:
        for key, item in mapping.items():
            key_part = str(key)
            path = key_part if not prefix else f"{prefix}.{key_part}"

            if isinstance(item, dict):
                if item:
                    walk(item, path)
                else:
                    flattened[path] = item
            else:
                flattened[path] = item

    walk(value, "")
    return flattened
