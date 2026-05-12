def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """Return True only if role exists and permission is explicitly assigned."""
    return role in matrix and permission in matrix[role]
