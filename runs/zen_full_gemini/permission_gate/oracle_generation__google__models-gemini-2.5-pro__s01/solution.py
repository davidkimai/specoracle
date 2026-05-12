"""
A module for checking role-based permissions.
"""

from typing import Dict, Set


def has_permission(
    matrix: Dict[str, Set[str]],
    role: str,
    permission: str,
) -> bool:
    """
    Checks if a role has a specific permission in a given permission matrix.

    This function implements a "deny by default" policy. If the role is not
    found in the matrix, or if the permission is not explicitly listed for
    the role, it returns False.

    Args:
        matrix: A dictionary mapping role names (str) to a set of
                permission names (set[str]).
        role: The name of the role to check.
        permission: The name of the permission to check.

    Returns:
        True if the role exists and has the specified permission,
        False otherwise.
    """
    permissions_for_role = matrix.get(role)

    if permissions_for_role is None:
        return False

    return permission in permissions_for_role
