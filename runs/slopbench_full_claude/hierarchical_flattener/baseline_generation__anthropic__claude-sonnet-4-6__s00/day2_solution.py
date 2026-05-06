"""
hierarchical_flattener.py

Provides flatten_paths(value: dict) -> dict[str, object], which flattens
nested dicts into dot-separated path keys.  Lists are treated as leaf values
by default; pass array_mode='index' to expand list items using bracket indexes.
"""

from __future__ import annotations


def flatten_paths(
    value: dict,
    _prefix: str = "",
    *,
    array_mode: str = "leaf",
) -> dict[str, object]:
    """Flatten a nested dict into a dict with dot-path keys.

    Parameters
    ----------
    value : dict
        The (possibly nested) dictionary to flatten.
    _prefix : str
        Internal parameter used during recursion to build the key prefix.
        Callers should not pass this argument.
    array_mode : str
        Controls how list values are handled.

        ``'leaf'`` (default)
            Lists are kept as-is (original behaviour).
        ``'index'``
            List items are expanded using bracket notation, e.g.
            ``users[0].name``.  Nested dicts and lists inside the expanded
            items are themselves flattened recursively.

    Returns
    -------
    dict[str, object]
        A flat dictionary whose keys are dot-separated paths corresponding to
        the original nested structure.

    Raises
    ------
    TypeError
        If *value* is not a dict.
    ValueError
        If *array_mode* is not ``'leaf'`` or ``'index'``.

    Examples
    --------
    >>> flatten_paths({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": [4, 5]}})
    {'x': [1, 2, 3], 'y.z': [4, 5]}

    >>> flatten_paths({"users": [{"name": "Alice"}, {"name": "Bob"}]}, array_mode='index')
    {'users[0].name': 'Alice', 'users[1].name': 'Bob'}
    """
    if not isinstance(value, dict):
        raise TypeError(
            f"flatten_paths expects a dict at the top level, got {type(value).__name__!r}"
        )
    if array_mode not in ("leaf", "index"):
        raise ValueError(f"array_mode must be 'leaf' or 'index', got {array_mode!r}")

    result: dict[str, object] = {}
    _flatten(value, _prefix, result, array_mode)
    return result


def _flatten(
    node: object,
    prefix: str,
    accumulator: dict[str, object],
    array_mode: str,
) -> None:
    """Recursive helper that writes flattened entries into *accumulator*."""
    if isinstance(node, dict):
        for key, child in node.items():
            full_key = f"{prefix}.{key}" if prefix else key
            _flatten(child, full_key, accumulator, array_mode)
    elif isinstance(node, list) and array_mode == "index":
        for idx, item in enumerate(node):
            full_key = f"{prefix}[{idx}]"
            _flatten(item, full_key, accumulator, array_mode)
    else:
        # Leaf value (including lists in 'leaf' mode, scalars, None, etc.)
        accumulator[prefix] = node
