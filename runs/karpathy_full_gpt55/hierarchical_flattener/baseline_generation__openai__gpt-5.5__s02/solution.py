from __future__ import annotations


def flatten_paths(value: dict) -> dict[str, object]:
    """
    Flatten a dictionary containing nested dictionaries into dot-path keys.

    Lists and all non-dictionary values are treated as leaf values.

    Example:
        {"a": {"b": 1}, "c": [2, 3]} -> {"a.b": 1, "c": [2, 3]}
    """
    if not isinstance(value, dict):
        raise TypeError("flatten_paths() expects a dict")

    flattened: dict[str, object] = {}

    def _flatten(current: dict, prefix: str) -> None:
        for key, item in current.items():
            if not isinstance(key, str):
                raise TypeError("all dictionary keys must be strings")

            path = key if prefix == "" else f"{prefix}.{key}"

            if isinstance(item, dict) and item:
                _flatten(item, path)
            else:
                if path in flattened:
                    raise ValueError(f"duplicate flattened path: {path!r}")
                flattened[path] = item

    _flatten(value, "")
    return flattened
