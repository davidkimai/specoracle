from __future__ import annotations

import re

_ALLOWED_FIELD_RE = re.compile(r"^[A-Za-z0-9_]+$")


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """
    Return valid field names from ``fields`` that are present in ``allowed``.

    A valid field contains only ASCII letters, digits, and underscores.
    Input order is preserved, and duplicates are removed.
    """
    sanitized: list[str] = []
    seen: set[str] = set()

    for field in fields:
        if field in seen:
            continue
        if field in allowed and _ALLOWED_FIELD_RE.fullmatch(field) is not None:
            sanitized.append(field)
            seen.add(field)

    return sanitized
