"""
hierarchical_flattener.py

Flatten nested dicts into dot-path keys.
Lists are treated as leaf values.
"""

from __future__ import annotations


def flatten_paths(value: dict, _prefix: str = "") -> dict[str, object]:
    """
    Recursively flatten a nested dictionary into a single-level dictionary
    whose keys are dot-separated paths to every leaf value.

    Parameters
    ----------
    value : dict
        The (possibly nested) dictionary to flatten.
    _prefix : str
        Internal parameter used during recursion to accumulate the current
        key path.  Callers should not pass this argument.

    Returns
    -------
    dict[str, object]
        A flat dictionary mapping dot-path strings to leaf values.
        Lists are considered leaf values and are not descended into.

    Examples
    --------
    >>> flatten_paths({"a": 1, "b": {"c": 2, "d": {"e": 3}}})
    {'a': 1, 'b.c': 2, 'b.d.e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": 4}})
    {'x': [1, 2, 3], 'y.z': 4}
    """
    if not isinstance(value, dict):
        raise TypeError(f"flatten_paths expects a dict, got {type(value).__name__!r}")

    result: dict[str, object] = {}

    for key, val in value.items():
        full_key = f"{_prefix}.{key}" if _prefix else str(key)

        if isinstance(val, dict):
            # Recurse into nested dicts
            nested = flatten_paths(val, _prefix=full_key)
            result.update(nested)
        else:
            # Everything else (including lists) is a leaf
            result[full_key] = val

    return result
