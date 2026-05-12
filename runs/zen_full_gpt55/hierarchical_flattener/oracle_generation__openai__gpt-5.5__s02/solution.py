from collections.abc import Mapping
from typing import Any


def flatten_paths(value: dict) -> dict[str, object]:
    """Flatten nested dictionaries into dot-separated path keys.

    Lists and all other non-dictionary values are treated as leaf values.
    """
    if not isinstance(value, dict):
        raise TypeError("flatten_paths() requires a dict")

    flattened: dict[str, object] = {}
    _flatten_mapping(value, prefix="", output=flattened)
    return flattened


def _flatten_mapping(
    mapping: Mapping[Any, Any],
    *,
    prefix: str,
    output: dict[str, object],
) -> None:
    for key, item in mapping.items():
        key_part = _validate_key(key)
        path = key_part if not prefix else f"{prefix}.{key_part}"

        if isinstance(item, dict) and item:
            _flatten_mapping(item, prefix=path, output=output)
            continue

        output[path] = item


def _validate_key(key: object) -> str:
    if not isinstance(key, str):
        raise TypeError("all dictionary keys must be strings")

    if key == "":
        raise ValueError("dictionary keys used in paths must not be empty")

    if "." in key:
        raise ValueError("dictionary keys used in paths must not contain '.'")

    return key
