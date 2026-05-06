def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """Return True only when role exists and permission is explicitly listed for it."""
    if not isinstance(matrix, dict):
        raise TypeError("matrix must be a dict")
    if not isinstance(role, str):
        raise TypeError("role must be a str")
    if not isinstance(permission, str):
        raise TypeError("permission must be a str")
    return permission in matrix.get(role, set())
