from typing import Set, List

__all__ = ["sanitize_fields"]


def _is_allowed_identifier(value: str) -> bool:
    return all(
        ("a" <= char <= "z")
        or ("A" <= char <= "Z")
        or ("0" <= char <= "9")
        or char == "_"
        for char in value
    )


def sanitize_fields(fields: List[str], allowed: Set[str]) -> List[str]:
    seen: set[str] = set()
    sanitized: list[str] = []

    for field in fields:
        if field in seen:
            continue
        if field in allowed and _is_allowed_identifier(field):
            seen.add(field)
            sanitized.append(field)

    return sanitized
