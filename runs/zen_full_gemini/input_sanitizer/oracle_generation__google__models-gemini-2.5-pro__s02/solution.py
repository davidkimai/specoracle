"""A module for sanitizing field names based on a whitelist and syntax rules."""

def _is_valid_field_syntax(field: str) -> bool:
    """
    Checks if a field contains only letters, digits, and underscores.

    An empty string is not considered a valid field.

    Args:
        field: The string to validate.

    Returns:
        True if the field has valid syntax, False otherwise.
    """
    if not field:
        return False
    return all(c.isalnum() or c == '_' for c in field)


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """
    Filters a list of fields, returning only those that are allowed and valid.

    The function preserves the order of the first appearance of each field
    from the input list and removes any duplicates.

    A field is considered valid if it is present in the `allowed` set and
    contains only letters, digits, and underscores.

    Args:
        fields: A list of strings representing the fields to sanitize.
        allowed: A set of strings representing the whitelist of allowed fields.

    Returns:
        A new list of sanitized, unique fields in their original order.

    Raises:
        TypeError: If `fields` is not a list, if any item in `fields` is not
                   a string, or if `allowed` is not a set.
    """
    if not isinstance(fields, list):
        raise TypeError("'fields' must be a list.")
    if not all(isinstance(f, str) for f in fields):
        raise TypeError("All items in 'fields' must be strings.")
    if not isinstance(allowed, set):
        raise TypeError("'allowed' must be a set.")

    sanitized_result = []
    seen = set()

    for field in fields:
        if field in seen:
            continue

        seen.add(field)

        is_allowed = field in allowed
        is_syntactically_valid = _is_valid_field_syntax(field)

        if is_allowed and is_syntactically_valid:
            sanitized_result.append(field)

    return sanitized_result
