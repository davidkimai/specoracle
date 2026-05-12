"""Permission gate module."""

__all__ = ["has_permission"]


def _require_string(value: object, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a str")


def _validate_matrix(matrix: object) -> None:
    if not isinstance(matrix, dict):
        raise TypeError("matrix must be a dict[str, set[str]]")

    for role, permissions in matrix.items():
        if not isinstance(role, str):
            raise TypeError("matrix roles must be str values")
        if not isinstance(permissions, set):
            raise TypeError("matrix permission collections must be set[str] values")
        for permission in permissions:
            if not isinstance(permission, str):
                raise TypeError("matrix permissions must be str values")


def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """Return True only when role exists and explicitly contains permission."""
    _validate_matrix(matrix)
    _require_string(role, "role")
    _require_string(permission, "permission")

    permissions = matrix.get(role)
    if permissions is None:
        return False

    return permission in permissions
