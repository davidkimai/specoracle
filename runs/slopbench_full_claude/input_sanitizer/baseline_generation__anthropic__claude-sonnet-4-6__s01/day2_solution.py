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
                     Fields whose names exceed their cap are omitted.
                     Fields without an entry in length_caps are unaffected.

    Returns:
        List of fields that pass the allowlist check, character validation, and
        (if applicable) the length cap, in original order, with duplicates removed.
    """
    valid_pattern = re.compile(r'^[A-Za-z0-9_]+$')
    seen = set()
    result = []
    for field in fields:
        if field in seen:
            continue
        seen.add(field)
        if field not in allowed:
            continue
        if not valid_pattern.match(field):
            continue
        if length_caps is not None and field in length_caps:
            if len(field) > length_caps[field]:
                continue
        result.append(field)
    return result
