"""
A module for checking role-based permissions.
"""

from __future__ import annotations

def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """
    Checks if a role has a specific permission based on a permissions matrix.

    This function enforces a "deny by default" policy. Permission is only granted
    if the role is explicitly defined in the matrix and the permission is
    explicitly listed for that role.

    Args:
        matrix: A dictionary where keys are role names (str) and values are
                sets of permission names (str) associated with that role.
        role: The name of the role to check.
        permission: The name of the permission to verify.

    Returns:
        True if the role exists in the matrix and has the specified permission.
        False in all other cases (e.g., role not found, permission not in
        the role's set).
    """
    permissions_for_role = matrix.get(role)
    if permissions_for_role is None:
        return False
    return permission in permissions_for_role
