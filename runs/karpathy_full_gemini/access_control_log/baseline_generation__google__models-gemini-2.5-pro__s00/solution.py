"""
A module for checking access control and logging attempts.
"""

from typing import Dict, List, Set, Any

def check_access(
    role: str,
    permission: str,
    matrix: Dict[str, Set[str]],
    log: List[Dict[str, Any]]
) -> bool:
    """
    Checks if a role has a specific permission and logs the attempt.

    This function implements a role-based access control (RBAC) check.
    It determines if the given `role` is granted the specified `permission`
    based on the provided access control `matrix`.

    The function adheres to a "deny by default" policy. If the role does not
    exist in the matrix, or if the permission is not explicitly granted to
    the role, access is denied.

    Every access attempt, whether successful or not, is recorded in the `log`
    list. The log entry is a dictionary containing the role, the requested
    permission, and the outcome of the check (allowed: True or False).

    Args:
        role: The role attempting to perform an action.
        permission: The permission required for the action.
        matrix: An access control matrix represented as a dictionary where
                keys are roles and values are sets of granted permissions.
        log: A list to which log entries of access attempts will be appended.
             This list is modified in-place.

    Returns:
        True if access is allowed, False otherwise.
    """
    allowed = False

    # Deny by default. Access is only granted if the role exists and the
    # permission is explicitly listed for that role.
    # Using .get() with a default empty set safely handles non-existent roles.
    role_permissions = matrix.get(role, set())
    if permission in role_permissions:
        allowed = True

    # Log every attempt with the final decision before returning.
    log_entry = {
        'role': role,
        'permission': permission,
        'allowed': allowed,
    }
    log.append(log_entry)

    return allowed
