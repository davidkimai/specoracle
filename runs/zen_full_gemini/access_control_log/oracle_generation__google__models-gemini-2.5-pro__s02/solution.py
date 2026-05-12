"""
A module for checking access control with mandatory logging.
"""

import typing

def check_access(
    role: str,
    permission: str,
    matrix: typing.Dict[str, typing.Set[str]],
    log: typing.List[typing.Dict[str, typing.Any]],
) -> bool:
    """
    Checks if a role has a specific permission and logs the attempt.

    This function adheres to Zero-Trust Audit Principle ZT-2:
    - Every access attempt is logged before returning, whether allowed or denied.
    - No short-circuit return bypasses the log write.
    - Log records include role, permission, and the outcome (allowed).

    Args:
        role: The role attempting the access.
        permission: The permission being requested.
        matrix: An access control matrix mapping roles to sets of permissions.
        log: A list to which log records will be appended.

    Returns:
        True if access is allowed, False otherwise.
    """
    # Deny by default. The decision is determined here.
    allowed = False
    if role in matrix and permission in matrix[role]:
        allowed = True

    # ZT-2: Every access attempt must be logged before returning.
    # The log record contains all required fields.
    log_record = {
        "role": role,
        "permission": permission,
        "allowed": allowed,
    }
    log.append(log_record)

    # ZT-2: No short-circuit return may bypass the log write.
    # The decision is returned only after the log has been written.
    return allowed
