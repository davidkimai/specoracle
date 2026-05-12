def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    return role in matrix and permission in matrix[role]
