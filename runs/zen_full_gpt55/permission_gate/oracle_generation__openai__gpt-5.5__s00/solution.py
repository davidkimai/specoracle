__all__ = ["has_permission"]


def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """Return whether a role explicitly has a permission.

    Unknown roles and unlisted permissions are denied by default.
    """
    if not isinstance(matrix, dict):
        raise TypeError("matrix must be a dict[str, set[str]]")
    if not isinstance(role, str):
        raise TypeError("role must be a str")
    if not isinstance(permission, str):
        raise TypeError("permission must be a str")

    if role not in matrix:
        return False

    permissions = matrix[role]
    if not isinstance(permissions, set):
        raise TypeError("matrix values must be set[str]")

    return permission in permissions
