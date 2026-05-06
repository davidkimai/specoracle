"""
hierarchical_flattener.py

Flatten a nested dict into a flat dict with dot-separated key paths.
Lists (and all other non-dict values) are treated as leaf values.
"""

from __future__ import annotations


def flatten_paths(value: dict, *, _prefix: str = "") -> dict[str, object]:
    """Return a flat dict whose keys are dot-joined paths from *value*.

    Args:
        value: A (possibly nested) dict to flatten.

    Returns:
        A flat dict mapping dot-path strings to leaf values.

    Raises:
        TypeError: If *value* is not a dict.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Expected a dict, got {type(value).__name__!r}")

    result: dict[str, object] = {}

    for key, val in value.items():
        if not isinstance(key, str):
            raise TypeError(f"All keys must be strings; got {type(key).__name__!r}")

        full_key = f"{_prefix}.{key}" if _prefix else key

        if isinstance(val, dict):
            nested = flatten_paths(val, _prefix=full_key)
            result.update(nested)
        else:
            result[full_key] = val

    return result
