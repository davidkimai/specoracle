"""
hierarchical_flattener.py

Flatten a nested dictionary into a flat dictionary with dot-separated keys.
Lists are treated as leaf values (not recursed into).
"""


def flatten_paths(value: dict) -> dict[str, object]:
    """Return a flat dict with dot-separated keys from a nested dict.

    Args:
        value: A (possibly nested) dictionary to flatten.

    Returns:
        A flat dictionary mapping dot-path strings to leaf values.

    Raises:
        TypeError: If *value* is not a dict.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Expected a dict, got {type(value).__name__!r}")

    result: dict[str, object] = {}
    _collect(value, prefix="", result=result)
    return result


def _collect(node: dict, prefix: str, result: dict[str, object]) -> None:
    """Recursively walk *node*, writing dot-path entries into *result*."""
    for key, val in node.items():
        if not isinstance(key, str):
            raise TypeError(f"Dict keys must be strings, got {type(key).__name__!r}")

        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(val, dict):
            _collect(val, prefix=full_key, result=result)
        else:
            result[full_key] = val
