from __future__ import annotations


def _require_string(value: object, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a str")


def _require_permission_set(value: object, role: str) -> set[str]:
    if not isinstance(value, set):
        raise TypeError(f"permissions for role {role!r} must be a set[str]")

    for permission in value:
        if not isinstance(permission, str):
            raise TypeError(f"permissions for role {role!r} must contain only str values")

    return value


def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    if not isinstance(matrix, dict):
        raise TypeError("matrix must be a dict[str, set[str]]")

    _require_string(role, "role")
    _require_string(permission, "permission")

    if role not in matrix:
        return False

    permissions = _require_permission_set(matrix[role], role)
    return permission in permissions
