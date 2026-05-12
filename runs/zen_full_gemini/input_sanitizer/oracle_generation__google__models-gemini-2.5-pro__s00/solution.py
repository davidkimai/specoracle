"""A module for sanitizing lists of field names."""

from typing import List, Set


def _is_valid_field_format(field: str) -> bool:
    """
    Check if a field contains only letters, digits, and underscores.

    An empty string or a non-string input is not considered a valid field.

    Args:
        field: The object to validate.

    Returns:
        True if the field is a string with a valid format, False otherwise.
    """
    if not isinstance(field, str) or not field:
        return False

    return all(char.isalnum() or char == '_' for char in field)


def sanitize_fields(fields: List[str], allowed: Set[str]) -> List[str]:
    """
    Filter a list of fields against a whitelist and format constraints.

    Returns a new list containing fields that are present in the `allowed` set
    and contain only letters, digits, and underscores. The order of the first
    appearance of each valid field is preserved, and duplicates are removed.
    Non-string items in the input list are ignored.

    Args:
        fields: A list of items to be sanitized, expected to be strings.
        allowed: A set of strings representing the whitelist of allowed fields.

    Returns:
        A new list containing the sanitized, unique, and ordered fields.

    Raises:
        TypeError: If `fields` is not a list or `allowed` is not a set.
    """
    if not isinstance(fields, list):
        raise TypeError("Input 'fields' must be a list.")
    if not isinstance(allowed, set):
        raise TypeError("Input 'allowed' must be a set.")

    sanitized_list = []
    seen = set()

    for field in fields:
        if field in seen:
            continue

        # A field is valid if it has the correct format and is in the whitelist.
        # The format check also handles non-string types gracefully.
        if _is_valid_field_format(field) and field in allowed:
            sanitized_list.append(field)
            seen.add(field)

    return sanitized_list
