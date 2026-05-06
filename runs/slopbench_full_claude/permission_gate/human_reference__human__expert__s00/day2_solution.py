from __future__ import annotations


def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    explicit = permission in matrix.get(role, set())
    wildcard = permission in matrix.get("*", set())
    return explicit or wildcard
