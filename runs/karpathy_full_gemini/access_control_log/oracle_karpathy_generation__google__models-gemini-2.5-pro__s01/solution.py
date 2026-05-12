import typing

def check_access(
    role: str,
    permission: str,
    matrix: typing.Dict[str, typing.Set[str]],
    log: typing.List[typing.Dict[str, typing.Any]]
) -> bool:
    """
    Checks if a role has a specific permission and logs the attempt.

    This function adheres to the Zero-Trust Audit Principle ZT-2:
    - Every access attempt is logged before returning, whether allowed or denied.
    - No short-circuit return bypasses the log write.
    - Log records include role, permission, and the outcome (allowed).

    Args:
        role: The role attempting the access.
        permission: The permission being requested.
        matrix: A dictionary mapping roles to sets of allowed permissions.
        log: A list to which the log record will be appended.

    Returns:
        True if access is allowed, False otherwise.
    """
    # Determine if the access should be allowed based on the matrix.
    # This calculation is performed first, establishing the decision.
    # Deny by default is implicit in this logic.
    permissions_for_role = matrix.get(role, set())
    allowed = permission in permissions_for_role

    # Create the log record with all required information.
    # This must be done for every attempt, regardless of the outcome.
    log_record = {
        "role": role,
        "permission": permission,
        "allowed": allowed,
    }

    # Append the record to the log. This must happen before returning.
    log.append(log_record)

    # Return the final decision after logging is complete.
    # This single return point ensures logging is never bypassed.
    return allowed
