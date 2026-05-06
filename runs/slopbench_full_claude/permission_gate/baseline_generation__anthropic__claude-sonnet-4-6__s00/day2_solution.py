def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    if role not in matrix and '*' not in matrix:
        return False
    role_permissions = matrix.get(role, set())
    wildcard_permissions = matrix.get('*', set())
    return permission in role_permissions or permission in wildcard_permissions
