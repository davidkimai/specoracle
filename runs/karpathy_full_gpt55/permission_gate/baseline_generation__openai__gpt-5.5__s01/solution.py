"""Permission gate module."""

from __future__ import annotations


def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """Return True only if the role exists and explicitly includes the permission."""
    if role not in matrix:
        return False

    permissions = matrix[role]
    if not isinstance(permissions, set):
        return False

    return permission in permissions


__all__ = ["has_permission"]
