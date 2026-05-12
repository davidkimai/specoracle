"""
A module for checking role-based permissions.
"""

from typing import Dict, Set


def has_permission(matrix: Dict[str, Set[str]], role: str, permission: str) -> bool:
    """
    Checks if a role has a specific permission based on a permission matrix.

    This function enforces a "deny by default" policy. Permission is granted
    only if the role is explicitly defined in the matrix and the permission is
    explicitly listed for that role.

    Args:
        matrix: A dictionary where keys are role names (str) and values are
                sets of permission names (str) granted to that role.
        role: The name of the role to check.
        permission: The name of the permission to check.

    Returns:
        True if the role exists and has the specified permission, False otherwise.
    """
    # The logic short-circuits: if the role is not in the matrix, the second
    # part of the 'and' condition is not evaluated, correctly returning False.
    return role in matrix and permission in matrix[role]
