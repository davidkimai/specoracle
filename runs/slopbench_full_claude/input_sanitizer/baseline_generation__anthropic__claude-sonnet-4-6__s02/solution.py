import re


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """Return fields that are in allowed and contain only letters, digits, and underscores.

    Preserves input order and removes duplicates.

    Args:
        fields: List of field name strings to sanitize.
        allowed: Set of allowed field names.

    Returns:
        List of fields that pass both the allowlist check and the character validation,
        in original order, without duplicates.
    """
    valid_pattern = re.compile(r'^\w+$')
    seen: set[str] = set()
    result: list[str] = []

    for field in fields:
        if field in seen:
            continue
        seen.add(field)
        if field in allowed and valid_pattern.match(field):
            result.append(field)

    return result
