"""
A module for checking access permissions and logging attempts.
"""

from typing import Dict, List, Set

def check_access(
    role: str,
    permission: str,
    matrix: Dict[str, Set[str]],
    log: List[Dict[str, any]]
) -> bool:
    """
    Checks if a role has a specific permission and logs the attempt.

    This function implements a "deny by default" policy. Access is granted
    only if the role is explicitly defined in the matrix and the requested
    permission is associated with that role.

    Every access check, whether successful or not, is recorded in the provided
    log list.

    Args:
        role: The role requesting access (e.g., 'admin', 'user').
        permission: The permission being requested (e.g., 'read', 'write').
        matrix: An access control matrix represented as a dictionary where keys
                are role names and values are sets of permission strings.
        log: A list that will be used to store log entries. Each entry is a
             dictionary containing the role, permission, and the outcome.

    Returns:
        True if the role has the specified permission, False otherwise.
    """
    allowed = False

    # Determine if access is allowed.
    # The check `role in matrix` prevents a KeyError if the role is unknown.
    if role in matrix and permission in matrix[role]:
        allowed = True

    # Log the access attempt before returning the decision.
    log_entry = {
        'role': role,
        'permission': permission,
        'allowed': allowed,
    }
    log.append(log_entry)

    return allowed
