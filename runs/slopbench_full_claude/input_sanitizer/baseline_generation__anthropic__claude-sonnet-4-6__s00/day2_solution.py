import re


def sanitize_fields(
    fields: list[str],
    allowed: set[str],
    length_caps: dict[str, int] | None = None,
) -> list[str]:
    """
    Return fields that are in allowed and contain only letters, digits,
    and underscores. Preserve input order and remove duplicates.

    If length_caps is provided and a field has an entry in it, the field
    is omitted when its name length exceeds the cap value.
    """
    pattern = re.compile(r'^\w+$')
    seen = set()
    result = []
    for field in fields:
        if field in seen:
            continue
        if field in allowed and pattern.match(field):
            if length_caps is not None and field in length_caps:
                if len(field) > length_caps[field]:
                    continue
            result.append(field)
            seen.add(field)
    return result
