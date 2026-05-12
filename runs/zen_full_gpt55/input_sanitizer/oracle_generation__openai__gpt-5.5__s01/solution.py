from __future__ import annotations

_ASCII_LETTERS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
_ASCII_DIGITS = frozenset("0123456789")
_ALLOWED_CHARACTERS = _ASCII_LETTERS | _ASCII_DIGITS | frozenset("_")


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """Return safe, allowed field names in input order without duplicates."""
    _require_list_of_strings(fields, "fields")
    _require_set_of_strings(allowed, "allowed")

    sanitized: list[str] = []
    seen: set[str] = set()

    for field in fields:
        if field in seen:
            continue
        if field not in allowed:
            continue
        if not _is_safe_field(field):
            continue

        sanitized.append(field)
        seen.add(field)

    return sanitized


def _require_list_of_strings(value: object, name: str) -> None:
    if not isinstance(value, list):
        raise TypeError(f"{name} must be a list[str]")

    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise TypeError(f"{name}[{index}] must be str")


def _require_set_of_strings(value: object, name: str) -> None:
    if not isinstance(value, set):
        raise TypeError(f"{name} must be a set[str]")

    for item in value:
        if not isinstance(item, str):
            raise TypeError(f"{name} must contain only str values")


def _is_safe_field(field: str) -> bool:
    if not field:
        return False

    return all(character in _ALLOWED_CHARACTERS for character in field)
