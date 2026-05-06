"""
access_control_log.py

Zero-Trust access control with mandatory audit logging (ZT-2).
Every access attempt is logged with role, permission, and allowed
before the decision is returned.
"""


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
    include_reason: bool = False,
) -> bool:
    """
    Check whether *role* holds *permission* according to *matrix*.

    The decision is deny-by-default: allowed is True only when the role
    exists in the matrix and the permission is present in its set.

    A log record is appended to *log* unconditionally before returning.
    No code path may return without having written the record first
    (ZT-2: no short-circuit return may bypass the log write).

    Parameters
    ----------
    role:           The role identifier being checked.
    permission:     The permission being requested.
    matrix:         Mapping of role → set of permitted permission strings.
    log:            Mutable list to which the audit record is appended.
    include_reason: When True, add a 'reason' key to the log record with
                    one of 'allowed', 'unknown_role', or 'missing_permission'.

    Returns
    -------
    bool: True if access is allowed, False otherwise.
    """
    if role not in matrix:
        allowed = False
        reason = "unknown_role"
    elif permission not in matrix[role]:
        allowed = False
        reason = "missing_permission"
    else:
        allowed = True
        reason = "allowed"

    record: dict = {
        "role": role,
        "permission": permission,
        "allowed": allowed,
    }

    if include_reason:
        record["reason"] = reason

    log.append(record)

    return allowed
