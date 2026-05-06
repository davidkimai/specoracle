def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """Return True when role exists and permission is explicitly listed for it,
    or when the wildcard role '*' grants that permission to all roles."""
    wildcard_grants = permission in matrix.get('*', set())
    if role not in matrix:
        return wildcard_grants
    return permission in matrix[role] or wildcard_grants
