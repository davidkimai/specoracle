"""
An access control module that enforces logging before returning a decision.

This module provides a function `check_access` that verifies if a given role
has a specific permission based on an access control matrix. It strictly
adheres to the Zero-Trust Audit Principle ZT-2, ensuring every access attempt
is logged before the access decision is returned.
"""

from typing import Any, Dict, List, Set


def check_access(
    role: str,
    permission: str,
    matrix: Dict[str, Set[str]],
    log: List[Dict[str, Any]],
) -> bool:
    """
    Checks if a role has a specific permission and logs the attempt.

    This function determines access based on the provided matrix and adheres to
    the Zero-Trust Audit Principle ZT-2 by logging every attempt before
    returning the decision. Access is denied by default if the role or
    permission is not found.

    Args:
        role: The role attempting to perform an action.
        permission: The permission required for the action.
        matrix: A dictionary mapping roles to a set of their permissions.
        log: A list to which the log record of the access attempt will be
             appended. The log record is a dictionary containing 'role',
             'permission', and 'allowed'.

    Returns:
        True if the role has the permission, False otherwise.
    """
    # Determine if the access is allowed. Deny by default.
    # The use of .get() provides a safe way to handle roles not in the matrix,
    # returning an empty set in that case.
    allowed = permission in matrix.get(role, set())

    # Create the log record. The record must contain the role, the permission
    # requested, and the outcome of the access check.
    log_entry = {
        'role': role,
        'permission': permission,
        'allowed': allowed,
    }

    # Log the access attempt. This action is performed unconditionally before
    # the function returns, fulfilling the ZT-2 principle.
    log.append(log_entry)

    # Return the final access decision. This is the single point of exit.
    return allowed
