"""
A module for checking role-based permissions against a permission matrix.
"""

from typing import Dict, Set


def has_permission(matrix: Dict[str, Set[str]], role: str, permission: str) -> bool:
    """
    Checks if a role has a specific permission in the given matrix.

    This function enforces a "deny by default" policy. Permission is granted
    only if the role is explicitly defined in the matrix and the permission
    is explicitly listed for that role.

    Args:
        matrix: A dictionary mapping role names to sets of permission strings.
                Example: {'admin': {'read', 'write'}, 'guest': {'read'}}
        role: The name of the role to check.
        permission: The name of the permission to check.

    Returns:
        True if the role has the permission, False otherwise.
    """
    # Using .get() with a default empty set elegantly handles the case
    # where the role does not exist in the matrix. If the role is not found,
    # the permission check is performed against an empty set, which will
    # always be False, thus denying by default.
    permissions_for_role = matrix.get(role, set())

    return permission in permissions_for_role
