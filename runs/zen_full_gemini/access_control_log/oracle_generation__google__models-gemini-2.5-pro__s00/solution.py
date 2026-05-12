"""
A module for access control with mandatory logging.

This module provides a function to check access permissions based on a role
and an access control matrix, ensuring that every attempt is logged.
"""

from typing import Dict, List, Set

def check_access(
    role: str,
    permission: str,
    matrix: Dict[str, Set[str]],
    log: List[Dict]
) -> bool:
    """
    Checks if a role has a specific permission and logs the attempt.

    This function adheres to Zero-Trust Audit Principle ZT-2:
    - Every access attempt is logged before returning.
    - No short-circuit return bypasses the log write.
    - Log records include role, permission, and the outcome (allowed).

    Args:
        role: The role requesting access.
        permission: The permission being requested.
        matrix: The access control matrix mapping roles to sets of permissions.
        log: A list to which the log record will be appended. The log record
             is a dictionary with 'role', 'permission', and 'allowed' keys.

    Returns:
        True if access is allowed, False otherwise.
    """
    allowed = False  # Deny by default.

    # Determine if access should be granted.
    # The check is performed by getting the set of permissions for the role
    # and then checking if the requested permission is in that set.
    # The .get() method with a default empty set handles cases where the role
    # is not in the matrix, correctly leading to a denial.
    permissions_for_role = matrix.get(role, set())
    if permission in permissions_for_role:
        allowed = True

    # Create and write the log record. This step is never bypassed, ensuring
    # that every access attempt is logged before the function returns.
    log_record = {
        'role': role,
        'permission': permission,
        'allowed': allowed,
    }
    log.append(log_record)

    return allowed
