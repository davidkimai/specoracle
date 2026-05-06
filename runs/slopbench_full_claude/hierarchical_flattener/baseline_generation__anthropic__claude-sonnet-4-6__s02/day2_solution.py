"""
hierarchical_flattener.py

Provides flatten_paths(value: dict) -> dict[str, object], which flattens
nested dictionaries into dot-separated key paths.  Lists are treated as
leaf values by default.

Day 2: Added array_mode parameter.  When array_mode='index', list items are
       flattened using bracket-index notation, e.g. users[0].name.
       The default array_mode='leaf' preserves the original behaviour.
"""

from __future__ import annotations

_VALID_ARRAY_MODES = frozenset({"leaf", "index"})


def flatten_paths(
    value: dict,
    _prefix: str = "",
    *,
    array_mode: str = "leaf",
) -> dict[str, object]:
    """Flatten a nested dictionary into a single-level dict with dot-path keys.

    Parameters
    ----------
    value : dict
        The (possibly nested) dictionary to flatten.
    _prefix : str
        Internal parameter used during recursion to carry the current path
        prefix.  Callers should not supply this argument.
    array_mode : str
        Controls how list values are handled.

        ``'leaf'`` (default)
            Lists are treated as opaque leaf values and are not recursed into.
            This preserves the original behaviour.

        ``'index'``
            Each list item is flattened using bracket-index notation.
            For example, a list at key ``users`` becomes ``users[0]``,
            ``users[1]``, etc.  If a list item is itself a dict, its keys
            are further flattened with a dot separator (``users[0].name``).
            Nested lists are handled recursively with the same rules.

    Returns
    -------
    dict[str, object]
        A flat dictionary whose keys are dot-joined paths and whose values
        are the leaf values from the original structure.

    Examples
    --------
    >>> flatten_paths({"a": {"b": 1, "c": {"d": 2}}, "e": 3})
    {'a.b': 1, 'a.c.d': 2, 'e': 3}

    >>> flatten_paths({"x": [1, 2, 3], "y": {"z": [4, 5]}})
    {'x': [1, 2, 3], 'y.z': [4, 5]}

    >>> flatten_paths({"users": [{"name": "Alice"}, {"name": "Bob"}]},
    ...               array_mode='index')
    {'users[0].name': 'Alice', 'users[1].name': 'Bob'}

    >>> flatten_paths({"nums": [1, 2, 3]}, array_mode='index')
    {'nums[0]': 1, 'nums[1]': 2, 'nums[2]': 3}
    """
    if not isinstance(value, dict):
        raise TypeError(
            f"flatten_paths expects a dict as its first argument, got {type(value).__name__!r}"
        )
    if array_mode not in _VALID_ARRAY_MODES:
        raise ValueError(
            f"array_mode must be one of {sorted(_VALID_ARRAY_MODES)!r}, got {array_mode!r}"
        )

    result: dict[str, object] = {}

    for key, val in value.items():
        full_key = f"{_prefix}.{key}" if _prefix else str(key)

        if isinstance(val, dict):
            nested = flatten_paths(val, _prefix=full_key, array_mode=array_mode)
            result.update(nested)
        elif isinstance(val, list) and array_mode == "index":
            _flatten_list(val, full_key, result, array_mode=array_mode)
        else:
            # Leaf value (includes lists in 'leaf' mode, scalars, None, etc.)
            result[full_key] = val

    return result


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _flatten_list(
    lst: list,
    prefix: str,
    result: dict[str, object],
    *,
    array_mode: str,
) -> None:
    """Recursively flatten a list into *result* using bracket-index notation.

    Parameters
    ----------
    lst : list
        The list to flatten.
    prefix : str
        The key path accumulated so far (e.g. ``"users"``).
    result : dict
        The output dictionary that entries are written into.
    array_mode : str
        Forwarded to recursive dict flattening calls.
    """
    for idx, item in enumerate(lst):
        indexed_key = f"{prefix}[{idx}]"

        if isinstance(item, dict):
            nested = flatten_paths(item, _prefix=indexed_key, array_mode=array_mode)
            result.update(nested)
        elif isinstance(item, list):
            _flatten_list(item, indexed_key, result, array_mode=array_mode)
        else:
            result[indexed_key] = item
