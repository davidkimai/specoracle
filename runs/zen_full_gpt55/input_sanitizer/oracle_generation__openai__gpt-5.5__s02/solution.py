from __future__ import annotations

import string


_ALLOWED_FIELD_CHARACTERS = frozenset(string.ascii_letters + string.digits + "_")


def _validate_inputs(fields: list[str], allowed: set[str]) -> None:
    if not isinstance(fields, list):
        raise TypeError("fields must be a list of strings")

    if not isinstance(allowed, set):
        raise TypeError("allowed must be a set of strings")

    if not all(isinstance(field, str) for field in fields):
        raise TypeError("fields must contain only strings")

    if not all(isinstance(field, str) for field in allowed):
        raise TypeError("allowed must contain only strings")


def _is_safe_field(field: str) -> bool:
    return bool(field) and all(character in _ALLOWED_FIELD_CHARACTERS for character in field)


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    _validate_inputs(fields, allowed)

    sanitized: list[str] = []
    seen: set[str] = set()

    for field in fields:
        if field in seen:
            continue

        if field in allowed and _is_safe_field(field):
            sanitized.append(field)
            seen.add(field)

    return sanitized
