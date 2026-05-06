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

    If length_caps is provided and a field has an entry in it, the field is
    omitted when its name length exceeds the cap value.
    """
    seen = set()
    result = []
    for field in fields:
        if field in seen:
            continue
        seen.add(field)
        if field not in allowed or not _is_valid_field(field):
            continue
        if length_caps is not None and field in length_caps:
            if len(field) > length_caps[field]:
                continue
        result.append(field)
    return result
