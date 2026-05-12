from __future__ import annotations

__all__ = ["flatten_paths"]


def flatten_paths(value: dict) -> dict[str, object]:
    """
    Flatten a nested dictionary into a dictionary keyed by dot-separated paths.

    Nested dictionaries are expanded into path components. Lists and all other
    non-dictionary values are treated as leaf values.

    Example:
        {"a": {"b": 1}, "c": [2, 3]} -> {"a.b": 1, "c": [2, 3]}
    """
    if not isinstance(value, dict):
        raise TypeError("flatten_paths() expects a dict")

    flattened: dict[str, object] = {}

    def visit(current: dict, prefix: str) -> None:
        for key, item in current.items():
            key_part = str(key)
            path = f"{prefix}.{key_part}" if prefix else key_part

            if isinstance(item, dict):
                visit(item, path)
            else:
                flattened[path] = item

    visit(value, "")
    return flattened
