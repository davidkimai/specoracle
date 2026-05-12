from __future__ import annotations


def flatten_paths(value: dict) -> dict[str, object]:
    """Flatten nested dictionaries into dot-separated path keys.

    Lists and all non-dict values are treated as leaf values.

    Example:
        {"a": {"b": 1}, "c": [2, 3]} -> {"a.b": 1, "c": [2, 3]}
    """
    if not isinstance(value, dict):
        raise TypeError("flatten_paths() requires a dict")

    flattened: dict[str, object] = {}
    _flatten_into(value, prefix="", output=flattened)
    return flattened


def _flatten_into(value: dict, prefix: str, output: dict[str, object]) -> None:
    for key, item in value.items():
        _validate_key(key)

        path = key if not prefix else f"{prefix}.{key}"

        if isinstance(item, dict):
            _flatten_into(item, prefix=path, output=output)
            continue

        output[path] = item


def _validate_key(key: object) -> None:
    if not isinstance(key, str):
        raise TypeError("flatten_paths() requires all dictionary keys to be strings")

    if key == "":
        raise ValueError("flatten_paths() does not support empty dictionary keys")
