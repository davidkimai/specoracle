"""
hierarchical_flattener.py

Flatten a nested dict into a flat dict with dot-separated key paths.
Lists (and all other non-dict values) are treated as leaf values by default.

Day 2: added *array_mode* parameter.
  - 'leaf'  (default) – lists are treated as opaque leaf values (original behaviour).
  - 'index' – list items are recursively flattened using bracket notation,
               e.g. ``users[0].name``.
"""

from __future__ import annotations


def flatten_paths(
    value: dict,
    *,
    _prefix: str = "",
    array_mode: str = "leaf",
) -> dict[str, object]:
    """Return a flat dict whose keys are dot-joined paths from *value*.

    Args:
        value:      A (possibly nested) dict to flatten.
        array_mode: Controls list handling.
                    ``'leaf'``  – lists are stored as-is (default).
                    ``'index'`` – lists are expanded with ``key[n]`` notation.

    Returns:
        A flat dict mapping dot-path strings to leaf values.

    Raises:
        TypeError:  If *value* is not a dict, or any key is not a string.
        ValueError: If *array_mode* is not ``'leaf'`` or ``'index'``.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Expected a dict, got {type(value).__name__!r}")

    if array_mode not in ("leaf", "index"):
        raise ValueError(f"array_mode must be 'leaf' or 'index'; got {array_mode!r}")

    result: dict[str, object] = {}

    for key, val in value.items():
        if not isinstance(key, str):
            raise TypeError(f"All keys must be strings; got {type(key).__name__!r}")

        full_key = f"{_prefix}.{key}" if _prefix else key

        if isinstance(val, dict):
            nested = flatten_paths(val, _prefix=full_key, array_mode=array_mode)
            result.update(nested)
        elif isinstance(val, list) and array_mode == "index":
            _flatten_list(val, prefix=full_key, result=result, array_mode=array_mode)
        else:
            result[full_key] = val

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _flatten_list(
    lst: list,
    *,
    prefix: str,
    result: dict[str, object],
    array_mode: str,
) -> None:
    """Recursively expand *lst* into *result* using ``prefix[n]`` keys."""
    for idx, item in enumerate(lst):
        indexed_key = f"{prefix}[{idx}]"
        if isinstance(item, dict):
            nested = flatten_paths(item, _prefix=indexed_key, array_mode=array_mode)
            result.update(nested)
        elif isinstance(item, list) and array_mode == "index":
            _flatten_list(item, prefix=indexed_key, result=result, array_mode=array_mode)
        else:
            result[indexed_key] = item
