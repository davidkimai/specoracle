from __future__ import annotations


def sanitize_fields(
    fields: list[str],
    allowed: set[str],
    length_caps: dict[str, int] | None = None,
) -> list[str]:
    clean: list[str] = []
    seen: set[str] = set()
    for field in fields:
        if field in seen:
            continue
        if field not in allowed:
            continue
        if not field.replace('_', '').isalnum():
            continue
        if length_caps is not None and field in length_caps:
            if len(field) > length_caps[field]:
                continue
        seen.add(field)
        clean.append(field)
    return clean
