import re

_VALID_PATTERN = re.compile(r'^\w+$')


def _is_valid_field(field: str) -> bool:
    return bool(_VALID_PATTERN.match(field))


def sanitize_fields(
    fields: list[str],
    allowed: set[str],
    length_caps: dict[str, int] | None = None,
) -> list[str]:
    """Return fields that are in allowed and contain only letters, digits, and underscores.

    Preserves input order and removes duplicates.

    If length_caps is provided, any field whose name length exceeds its cap value
    is omitted.
    """
    seen = set()
    result = []
    for field in fields:
        if field in seen:
            continue
        seen.add(field)
        if field not in allowed:
            continue
        if not _is_valid_field(field):
            continue
        if length_caps is not None and field in length_caps:
            if len(field) > length_caps[field]:
                continue
        result.append(field)
    return result
