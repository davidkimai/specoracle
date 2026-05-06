"""
input_sanitizer.py

Provides sanitize_fields: filters a list of field names against an allowed set
and a safe-character constraint, preserving order and removing duplicates.
"""

import re

_SAFE_PATTERN = re.compile(r'^\w+$')  # letters, digits, underscores only


def _is_safe(field: str) -> bool:
    """Return True if field contains only letters, digits, and underscores."""
    return bool(_SAFE_PATTERN.match(field))


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """
    Return fields that are present in allowed and contain only safe characters.

    Args:
        fields:  Ordered list of candidate field names.
        allowed: Set of permitted field names.

    Returns:
        Deduplicated, order-preserving list of accepted field names.

    Raises:
        TypeError: If fields is not a list or allowed is not a set.
    """
    if not isinstance(fields, list):
        raise TypeError(f"fields must be a list, got {type(fields).__name__!r}")
    if not isinstance(allowed, set):
        raise TypeError(f"allowed must be a set, got {type(allowed).__name__!r}")

    seen: set[str] = set()
    result: list[str] = []

    for field in fields:
        if not isinstance(field, str):
            raise TypeError(f"each field must be a str, got {type(field).__name__!r}")
        if field in seen:
            continue
        seen.add(field)
        if field in allowed and _is_safe(field):
            result.append(field)

    return result
