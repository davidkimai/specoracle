"""
hierarchical_flattener.py

Provides flatten_paths(value: dict) -> dict[str, object].

Flattens nested dictionaries into dot-separated key paths.
Lists and all other non-dict values are treated as leaf values.
"""

from __future__ import annotations


def flatten_paths(value: dict, _prefix: str = "") -> dict[str, object]:
    """Flatten a nested dictionary into dot-path keys.

    Parameters
    ----------
    value:
        The (possibly nested) dictionary to flatten.
    _prefix:
        Internal parameter used during recursion to carry the current
        key prefix.  Callers should not supply this argument.

    Returns
    -------
    dict[str, object]
        A new flat dictionary whose keys are dot-joined paths from the
        original nested structure and whose values are the leaf values
        (anything that is not a ``dict``).

    Examples
    --------
    >>> flatten_paths({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": [4, 5]}})
    {'x': [1, 2, 3], 'y.z': [4, 5]}

    >>> flatten_paths({})
    {}
    """
    if not isinstance(value, dict):
        raise TypeError(f"flatten_paths expects a dict at the top level, got {type(value).__name__!r}")

    result: dict[str, object] = {}

    for key, val in value.items():
        full_key = f"{_prefix}.{key}" if _prefix else str(key)

        if isinstance(val, dict):
            # Recurse into nested dicts
            nested = flatten_paths(val, _prefix=full_key)
            if nested:
                result.update(nested)
            else:
                # Empty dict is itself a leaf
                result[full_key] = val
        else:
            # Everything else (including lists) is a leaf value
            result[full_key] = val

    return result
