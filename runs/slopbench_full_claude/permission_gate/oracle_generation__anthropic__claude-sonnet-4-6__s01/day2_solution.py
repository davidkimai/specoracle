def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """Return True only when role exists and permission is explicitly listed for it,
    or when the wildcard role '*' grants the permission to all roles."""
    if not isinstance(matrix, dict):
        raise TypeError("matrix must be a dict")
    if not isinstance(role, str):
        raise TypeError("role must be a str")
    if not isinstance(permission, str):
        raise TypeError("permission must be a str")

    role_permissions = matrix.get(role)
    if role_permissions is not None and permission in role_permissions:
        return True

    wildcard_permissions = matrix.get("*")
    if wildcard_permissions is not None and permission in wildcard_permissions:
        return True

    return False
