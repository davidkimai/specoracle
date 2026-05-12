"""
A module for checking role-based permissions.
"""

from typing import Dict, Set

def has_permission(matrix: Dict[str, Set[str]], role: str, permission: str) -> bool:
    """
    Checks if a role has a specific permission based on a permission matrix.

    This function follows a "deny by default" policy. Permission is granted
    only if the role is explicitly defined in the matrix and the requested
    permission is explicitly listed for that role.

    Args:
        matrix: A dictionary mapping roles (str) to a set of their
                permissions (str).
        role: The role to check.
        permission: The permission to check for.

    Returns:
        True if the role has the permission, False otherwise.
    """
    # Safely get the set of permissions for the given role.
    # If the role does not exist in the matrix, .get() returns None.
    permissions_for_role = matrix.get(role)

    # If the role doesn't exist, deny permission by default.
    if permissions_for_role is None:
        return False

    # If the role exists, check if the specific permission is in its set.
    return permission in permissions_for_role
