from __future__ import annotations

__all__ = ["sanitize_fields"]


def _is_allowed_identifier_char(char: str) -> bool:
    return (
        "A" <= char <= "Z"
        or "a" <= char <= "z"
        or "0" <= char <= "9"
        or char == "_"
    )


def _is_safe_field(field: str) -> bool:
    return bool(field) and all(_is_allowed_identifier_char(char) for char in field)


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """
    Return allowed, syntactically safe field names in input order without duplicates.

    A safe field contains only ASCII letters, ASCII digits, and underscores.
    """
    sanitized: list[str] = []
    seen: set[str] = set()

    for field in fields:
        if field in seen:
            continue
        if field in allowed and _is_safe_field(field):
            sanitized.append(field)
            seen.add(field)

    return sanitized
