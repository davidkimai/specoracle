"""
A module for performing and logging access control checks.

This module provides a function `check_access` that evaluates access requests
based on a role-permission matrix and logs every attempt, ensuring compliance
with the Zero-Trust Audit Principle ZT-2.
"""

import typing

def check_access(
    role: str,
    permission: str,
    matrix: typing.Dict[str, typing.Set[str]],
    log: typing.List[typing.Dict[str, typing.Any]]
) -> bool:
    """
    Checks if a role has a specific permission and logs the attempt.

    Args:
        role: The role attempting to perform an action.
        permission: The permission required for the action.
        matrix: An access control matrix mapping roles to sets of permissions.
        log: A mutable list to which log records will be appended.

    Returns:
        True if access is allowed, False otherwise.
    """
    # Determine the access decision. Deny by default.
    # The use of .get() with a default empty set safely handles cases where
    # the role does not exist in the matrix.
    permissions_for_role = matrix.get(role, set())
    allowed = permission in permissions_for_role

    # Per ZT-2, create the log record with role, permission, and the
    # final decision.
    log_record = {
        'role': role,
        'permission': permission,
        'allowed': allowed,
    }

    # Per ZT-2, every access attempt must be logged before returning, whether
    # allowed or denied. This structure with a single return at the end
    # ensures the log write is never bypassed by a short-circuit.
    log.append(log_record)

    return allowed
