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


def sanitize_fields(
    fields: list[str],
    allowed: set[str],
    length_caps: dict[str, int] | None = None,
) -> list[str]:
    """
    Return fields that are present in allowed and contain only safe characters.

    Args:
        fields:      Ordered list of candidate field names.
        allowed:     Set of permitted field names.
        length_caps: Optional mapping of field name to maximum allowed length.
                     If a field appears in length_caps and its name exceeds the
                     cap, it is omitted.  Fields not present in length_caps are
                     unaffected.

    Returns:
        Deduplicated, order-preserving list of accepted field names.

    Raises:
        TypeError: If fields is not a list, allowed is not a set, or
                   length_caps is not a dict (when provided).
    """
    if not isinstance(fields, list):
        raise TypeError(f"fields must be a list, got {type(fields).__name__!r}")
    if not isinstance(allowed, set):
        raise TypeError(f"allowed must be a set, got {type(allowed).__name__!r}")
    if length_caps is not None and not isinstance(length_caps, dict):
        raise TypeError(
            f"length_caps must be a dict or None, got {type(length_caps).__name__!r}"
        )

    seen: set[str] = set()
    result: list[str] = []

    for field in fields:
        if not isinstance(field, str):
            raise TypeError(f"each field must be a str, got {type(field).__name__!r}")
        if field in seen:
            continue
        seen.add(field)
        if field not in allowed or not _is_safe(field):
            continue
        if length_caps is not None and field in length_caps:
            if len(field) > length_caps[field]:
                continue
        result.append(field)

    return result
