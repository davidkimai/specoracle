"""
A module for sanitizing input field names based on a strict allowlist
and character validation.
"""

import re
from typing import List, Set

# Pre-compiled regex for validating field names.
# A valid field must consist of one or more ASCII letters, digits, or underscores.
_VALID_FIELD_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


def sanitize_fields(fields: List[str], allowed: Set[str]) -> List[str]:
    """
    Sanitizes a list of field names.

    Filters the input list `fields` to include only those that are present in
    the `allowed` set and consist solely of letters, digits, and underscores.
    The order of the returned fields is preserved from their first appearance
    in the input, and duplicates are removed.

    Args:
        fields: A list of strings to be sanitized.
        allowed: A set of strings representing the allowlist of valid fields.

    Returns:
        A list of sanitized and unique field names, preserving original order.

    Example:
        >>> sanitize_fields(
        ...     ['user_id', 'name', 'email', 'invalid-field', 'user_id'],
        ...     {'user_id', 'name'}
        ... )
        ['user_id', 'name']
    """
    sanitized = []
    seen = set()

    for field in fields:
        if field in seen:
            continue

        # A field is valid if it's in the allowlist and matches the required pattern.
        # The regex ensures the string is non-empty and contains only valid characters.
        if field in allowed and _VALID_FIELD_PATTERN.fullmatch(field):
            sanitized.append(field)
            seen.add(field)

    return sanitized
