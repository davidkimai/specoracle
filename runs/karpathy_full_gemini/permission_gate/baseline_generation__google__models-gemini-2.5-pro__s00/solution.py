"""
A module for checking role-based permissions.
"""

def has_permission(matrix: dict[str, set[str]], role: str, permission: str) -> bool:
    """
    Checks if a role has a specific permission based on a permission matrix.

    This function enforces a "deny by default" policy. Access is granted
    only if the role is explicitly defined in the matrix and the requested
    permission is explicitly listed for that role.

    Args:
        matrix: A dictionary where keys are role names (str) and values are
                sets of permission names (str).
        role: The name of the role to check.
        permission: The name of the permission to check for.

    Returns:
        True if the role has the permission, False otherwise.
    """
    # Using .get() with a default empty set elegantly handles the case
    # where the role does not exist in the matrix. In that scenario,
    # the check `permission in set()` will correctly evaluate to False,
    # satisfying the "deny by default" requirement for unknown roles.
    permissions_for_role = matrix.get(role, set())
    return permission in permissions_for_role
