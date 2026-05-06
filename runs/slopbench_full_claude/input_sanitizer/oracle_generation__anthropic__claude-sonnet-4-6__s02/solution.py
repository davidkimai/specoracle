import re

_VALID_PATTERN = re.compile(r'^\w+$')


def _is_valid_field(field: str) -> bool:
    return bool(_VALID_PATTERN.match(field))


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """Return fields that are in allowed and contain only letters, digits, and underscores.

    Preserves input order and removes duplicates.
    """
    seen = set()
    result = []
    for field in fields:
        if field in seen:
            continue
        seen.add(field)
        if field in allowed and _is_valid_field(field):
            result.append(field)
    return result
