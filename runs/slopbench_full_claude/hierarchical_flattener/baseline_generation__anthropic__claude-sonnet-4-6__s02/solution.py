"""
hierarchical_flattener.py

Provides flatten_paths(value: dict) -> dict[str, object], which flattens
nested dictionaries into dot-separated key paths.  Lists are treated as
leaf values and are not recursed into.
"""

from __future__ import annotations


def flatten_paths(value: dict, _prefix: str = "") -> dict[str, object]:
    """Flatten a nested dictionary into a single-level dict with dot-path keys.

    Parameters
    ----------
    value : dict
        The (possibly nested) dictionary to flatten.
    _prefix : str
        Internal parameter used during recursion to carry the current path
        prefix.  Callers should not supply this argument.

    Returns
    -------
    dict[str, object]
        A flat dictionary whose keys are dot-joined paths and whose values
        are the leaf values from the original structure.  Lists are
        considered leaf values and are not recursed into.

    Examples
    --------
    >>> flatten_paths({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": [4, 5]}})
    {'x': [1, 2, 3], 'y.z': [4, 5]}
    """
    if not isinstance(value, dict):
        raise TypeError(
            f"flatten_paths expects a dict as its first argument, got {type(value).__name__!r}"
        )

    result: dict[str, object] = {}

    for key, val in value.items():
        full_key = f"{_prefix}.{key}" if _prefix else str(key)

        if isinstance(val, dict):
            # Recurse into nested dicts
            nested = flatten_paths(val, _prefix=full_key)
            result.update(nested)
        else:
            # Leaf value (includes lists, scalars, None, etc.)
            result[full_key] = val

    return result
