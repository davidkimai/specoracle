__all__ = ["sanitize_fields"]


def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    """Return allowed field names with safe characters, preserving order."""
    _validate_fields(fields)
    _validate_allowed(allowed)

    result: list[str] = []
    seen: set[str] = set()

    for field in fields:
        if field in seen:
            continue
        if field not in allowed:
            continue
        if not _has_only_safe_characters(field):
            continue

        seen.add(field)
        result.append(field)

    return result


def _validate_fields(fields: list[str]) -> None:
    if not isinstance(fields, list):
        raise TypeError("fields must be a list of strings")

    for index, field in enumerate(fields):
        if not isinstance(field, str):
            raise TypeError(f"fields[{index}] must be a string")


def _validate_allowed(allowed: set[str]) -> None:
    if not isinstance(allowed, set):
        raise TypeError("allowed must be a set of strings")

    for value in allowed:
        if not isinstance(value, str):
            raise TypeError("allowed must contain only strings")


def _has_only_safe_characters(value: str) -> bool:
    return all(character == "_" or character.isalnum() for character in value)
