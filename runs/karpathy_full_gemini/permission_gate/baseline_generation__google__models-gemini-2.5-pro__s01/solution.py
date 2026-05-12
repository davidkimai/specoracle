"""
A module for checking user permissions based on a role matrix.
"""

from typing import Dict, Set


def has_permission(matrix: Dict[str, Set[str]], role: str, permission: str) -> bool:
    """
    Checks if a role has a specific permission based on a permission matrix.

    This function follows a "deny by default" policy. It returns True only if
    the role is explicitly defined in the matrix and the permission is
    explicitly listed for that role. For any unknown role or permission, it
    returns False.

    Args:
        matrix: A dictionary representing the permission matrix. Keys are role
                names (str), and values are sets of permission names (str).
        role: The name of the role to check.
        permission: The name of the permission to check.

    Returns:
        True if the role has the permission, False otherwise.
    """
    # Retrieve the set of permissions for the given role.
    # If the role does not exist in the matrix, .get() returns an empty set
    # as a default. This elegantly handles the "deny by default" requirement
    # for unknown roles.
    permissions_for_role = matrix.get(role, set())

    # Check if the requested permission is present in the role's permission set.
    # If the role was unknown, this correctly checks against an empty set,
    # resulting in False.
    return permission in permissions_for_role
