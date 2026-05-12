"""
A module for checking role-based permissions against a permission matrix.
"""

from typing import Dict, Set


def has_permission(matrix: Dict[str, Set[str]], role: str, permission: str) -> bool:
    """
    Checks if a role has a specific permission based on a permission matrix.

    This function follows a "deny by default" policy. It returns True only
    if the role is explicitly defined in the matrix and the permission is
    explicitly granted to that role.

    Args:
        matrix: A dictionary where keys are role names (str) and values are
                sets of permission names (str) granted to that role.
        role: The name of the role to check.
        permission: The name of the permission to check for.

    Returns:
        bool: True if the role exists and has the specified permission,
              False otherwise.
    """
    permissions_for_role = matrix.get(role)

    # Return True only if the role exists (permissions_for_role is not None)
    # and the permission is in the set of permissions for that role.
    return permissions_for_role is not None and permission in permissions_for_role
