import re


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """
    Return fields that are in allowed and contain only letters, digits,
    and underscores. Preserve input order and remove duplicates.
    """
    pattern = re.compile(r'^[A-Za-z0-9_]+$')
    seen = set()
    result = []
    for field in fields:
        if field in seen:
            continue
        seen.add(field)
        if field in allowed and pattern.match(field):
            result.append(field)
    return result
