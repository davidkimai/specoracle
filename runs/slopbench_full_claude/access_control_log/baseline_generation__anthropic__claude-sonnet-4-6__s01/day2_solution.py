"""
access_control_log.py

Implements check_access with logging of every access attempt.
"""

from datetime import datetime, timezone


def check_access(
    role: str,
    permission: str,
    matrix: dict[str, set[str]],
    log: list[dict],
    include_reason: bool = False,
) -> bool:
    """
    Determine whether *role* holds *permission* according to *matrix*.

    Every call appends an entry to *log* with the keys:
        - timestamp : ISO-8601 UTC string
        - role      : the role that was checked
        - permission: the permission that was checked
        - allowed   : bool result of the check
        - reason    : (only present when include_reason=True)
                      'allowed', 'unknown_role', or 'missing_permission'

    Deny by default (i.e. when the role is absent or lacks the permission).

    Parameters
    ----------
    role:           The role to check.
    permission:     The permission to verify.
    matrix:         Mapping of role -> set of granted permissions.
    log:            Mutable list; an audit record is appended before returning.
    include_reason: When True, add a 'reason' key to the log record.

    Returns
    -------
    bool – True if access is granted, False otherwise.
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
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "role": role,
        "permission": permission,
        "allowed": allowed,
    }

    if include_reason:
        record["reason"] = reason

    log.append(record)

    return allowed
