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
    role:           The role whose access is being evaluated.
    permission:     The permission being requested.
    matrix:         Mapping of role -> set of granted permissions.
    log:            Mutable list; a record is appended before every return.
    include_reason: When True, a 'reason' key is added to the log record.
                    Possible values: 'allowed', 'unknown_role',
                    'missing_permission'.

    Returns
    -------
    bool: True if access is allowed, False otherwise (deny-by-default).
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

    # ZT-2: log must be written before returning, no short-circuit bypass.
    record: dict = {
        "role": role,
        "permission": permission,
        "allowed": allowed,
    }
    if include_reason:
        record["reason"] = reason

    log.append(record)

    return allowed
