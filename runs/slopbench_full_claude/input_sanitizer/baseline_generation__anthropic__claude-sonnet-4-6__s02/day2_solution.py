import re


def sanitize_fields(
    fields: list[str],
    allowed: set[str],
    length_caps: dict[str, int] | None = None,
) -> list[str]:
    """Return fields that are in allowed and contain only letters, digits, and underscores.

    Preserves input order and removes duplicates.

    Args:
        fields: List of field name strings to sanitize.
        allowed: Set of allowed field names.
        length_caps: Optional mapping of field name to maximum allowed length.
            If a field has an entry here and its name exceeds that length, it
            is omitted. Fields without an entry are unaffected.

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
            if length_caps is not None and field in length_caps:
                if len(field) > length_caps[field]:
                    continue
            result.append(field)

    return result
