"""
hierarchical_flattener.py

Flatten a nested dictionary into a flat dictionary with dot-separated keys.
Lists are treated as leaf values by default (array_mode='leaf').
When array_mode='index', list items are flattened using bracket indexes
such as users[0].name.
"""


def flatten_paths(value: dict, array_mode: str = "leaf") -> dict[str, object]:
    """Return a flat dict with dot-separated keys from a nested dict.

    Args:
        value: A (possibly nested) dictionary to flatten.
        array_mode: Controls list handling.
            'leaf'  – lists are treated as opaque leaf values (default).
            'index' – lists are recursed into using bracket notation,
                      e.g. key[0].subkey.

    Returns:
        A flat dictionary mapping dot-path strings to leaf values.

    Raises:
        TypeError: If *value* is not a dict.
        ValueError: If *array_mode* is not 'leaf' or 'index'.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Expected a dict, got {type(value).__name__!r}")
    if array_mode not in ("leaf", "index"):
        raise ValueError(f"array_mode must be 'leaf' or 'index', got {array_mode!r}")

    result: dict[str, object] = {}
    _collect(value, prefix="", result=result, array_mode=array_mode)
    return result


def _collect(
    node: dict,
    prefix: str,
    result: dict[str, object],
    array_mode: str,
) -> None:
    """Recursively walk *node*, writing dot-path entries into *result*."""
    for key, val in node.items():
        if not isinstance(key, str):
            raise TypeError(f"Dict keys must be strings, got {type(key).__name__!r}")

        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(val, dict):
            _collect(val, prefix=full_key, result=result, array_mode=array_mode)
        elif isinstance(val, list) and array_mode == "index":
            _collect_list(val, prefix=full_key, result=result, array_mode=array_mode)
        else:
            result[full_key] = val


def _collect_list(
    items: list,
    prefix: str,
    result: dict[str, object],
    array_mode: str,
) -> None:
    """Recursively walk a list, writing bracket-indexed dot-path entries."""
    for idx, val in enumerate(items):
        full_key = f"{prefix}[{idx}]"

        if isinstance(val, dict):
            _collect(val, prefix=full_key, result=result, array_mode=array_mode)
        elif isinstance(val, list) and array_mode == "index":
            _collect_list(val, prefix=full_key, result=result, array_mode=array_mode)
        else:
            result[full_key] = val
