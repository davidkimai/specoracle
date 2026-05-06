"""
hierarchical_flattener.py

Flatten nested dictionaries into dot-path keys.
Lists are treated as leaf values.
"""


def flatten_paths(value: dict, _prefix: str = "") -> dict:
    """
    Flatten a nested dictionary into a single-level dictionary with dot-separated keys.

    Parameters
    ----------
    value : dict
        The (possibly nested) dictionary to flatten.
    _prefix : str
        Internal parameter used during recursion to build the key path.
        Callers should not pass this argument.

    Returns
    -------
    dict[str, object]
        A flat dictionary where each key is a dot-separated path string
        representing the original nesting hierarchy, and each value is a
        non-dict leaf value (including lists, which are kept as-is).

    Examples
    --------
    >>> flatten_paths({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": [4, 5]}})
    {'x': [1, 2, 3], 'y.z': [4, 5]}
    """
    if not isinstance(value, dict):
        raise TypeError(f"flatten_paths expects a dict as its first argument, got {type(value).__name__!r}")

    result: dict = {}

    for key, val in value.items():
        full_key = f"{_prefix}.{key}" if _prefix else str(key)

        if isinstance(val, dict):
            # Recurse into nested dicts
            nested = flatten_paths(val, _prefix=full_key)
            result.update(nested)
        else:
            # Treat everything else (including lists) as a leaf value
            result[full_key] = val

    return result
