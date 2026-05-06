def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """Return True only when role exists and permission is explicitly listed for it."""
    if role not in matrix:
        return False
    return permission in matrix[role]
