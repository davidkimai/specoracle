"""
access_control_log.py

Zero-Trust access control with mandatory audit logging (ZT-2).
Every access attempt is logged before the decision is returned.
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

    Parameters
    ----------
    role           : The role identifier to check.
    permission     : The permission identifier to check.
    matrix         : Mapping of role -> set of permitted permissions.
    log            : Mutable list to which the audit record is appended.
    include_reason : When True, add a 'reason' key to the log record.
                     Possible values: 'allowed', 'unknown_role',
                     'missing_permission'.

    Returns
    -------
    bool : True if access is allowed, False otherwise.

    ZT-2 guarantee: the log record is written unconditionally before the
    function returns, regardless of the decision.
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
