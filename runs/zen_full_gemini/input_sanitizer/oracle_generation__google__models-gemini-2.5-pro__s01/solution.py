"""
A module for sanitizing field names based on an allowlist and format constraints.
"""

import re
from typing import List, Set

# A pre-compiled regex for validating field names.
# Field names must consist of only letters, digits, and underscores.
_FIELD_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


def _is_valid_field_format(field: str) -> bool:
    """
    Checks if a field name contains only letters, digits, and underscores.

    Args:
        field: The field name string to validate.

    Returns:
        True if the field name has a valid format, False otherwise.
    """
    if not isinstance(field, str):
        return False
    return _FIELD_NAME_PATTERN.match(field) is not None


def sanitize_fields(fields: List[str], allowed: Set[str]) -> List[str]:
    """
    Filters a list of fields against an allowed set and character constraints.

    The function returns fields that are present in the `allowed` set and
    contain only alphanumeric characters (letters, digits) and underscores.
    The order of the first appearance of valid fields from the input list is
    preserved, and duplicates are removed.

    Args:
        fields: A list of strings to be sanitized.
        allowed: A set of strings representing the allowed fields.

    Returns:
        A list of sanitized field names.

    Raises:
        TypeError: If `fields` is not a list, `allowed` is not a set, or if an
                   element in `fields` is not hashable (e.g., a list).
    """
    if not isinstance(fields, list):
        raise TypeError("Input 'fields' must be a list.")
    if not isinstance(allowed, set):
        raise TypeError("Input 'allowed' must be a set.")

    sanitized = []
    seen = set()

    for field in fields:
        if field in seen:
            continue

        is_allowed = field in allowed
        is_valid = _is_valid_field_format(field)

        if is_allowed and is_valid:
            sanitized.append(field)
            seen.add(field)

    return sanitized
